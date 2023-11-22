from datetime import datetime, timedelta
import asyncio
import time

from pyrogram import Client, filters
from pyrogram.types import Message
from sqlalchemy import select, func, insert

from config import API_ID, API_HASH, TG_USERNAME
from database.database import async_session_maker
from database.models import User
from loguru import logger


logger.add('logs.log', format='{time} {level} {message}', level='INFO', rotation='1 day')

app = Client(name='me', api_id=API_ID, api_hash=API_HASH)


# Проверка существования пользователя в базе данных
async def is_user_exists(telegram_id: str) -> bool:
    async with async_session_maker() as session:
        async with session.begin():
            query = select(func.count(User.id)).where(User.telegram_id == telegram_id)
            user_info = await session.execute(query)
            user_info = user_info.all()[0][0]

    return user_info


# Добавление пользователя, который нам написал в первый раз, в базу данных
async def add_user(telegram_id: str, username: str) -> None:
    async with async_session_maker() as session:
        async with session.begin():
            stmt = insert(User).values({
                'telegram_id': telegram_id,
                'username': username,
                'registration_date': datetime.utcnow().date()
            })
            await session.execute(stmt)
            await session.commit()
            logger.info(f'User {telegram_id} ({username}) registered')


# Старт воронки
# Отправка сообщений пользователю, который нам написал
async def start_funnel(client: Client, user_id: int, username: str, chat_id: int) -> None:
    await asyncio.sleep(600)
    await client.send_message(chat_id, 'Добрый день!')
    logger.info(f'Message to {user_id} ({username}) delivered')

    # не 5400, а 4800, потому что через 90 минут с начала воронки, т.е. через 80 минут после первого сообщения
    await asyncio.sleep(4800)
    await client.send_message(chat_id, 'Подготовила для вас материал')
    logger.info(f'Message to {user_id} ({username}) delivered')
    await client.send_photo(chat_id, photo='static/python.jpg')
    logger.info(f'Message to {user_id} ({username}) delivered')

    # если мы не отправили сообщение Хорошего дня,
    # то через 30 минут после второго сообщения отправляется сообщение
    # Скоро вернусь с новым материалом 1800
    my_messages = []
    time.sleep(1800)  # здесь используем time.sleep(),
    # потому что нам нужно считать историю сообщений спустя 30 минут после последнего сообщения
    # если бы делали asyncio.sleep(), то не учитывались бы последние сообщения
    async for message in app.get_chat_history(chat_id):
        if message.from_user.username == TG_USERNAME:
            my_messages.append(str(message.text))
    if my_messages[0] != 'Хорошего дня':
        await client.send_message(chat_id, 'Скоро вернусь с новым материалом!')
        logger.info(f'Message to {user_id} ({username}) delivered')


#  Обработчик сообщений от пользователей
#  Когда пользователь нам отправляет сообщение, запускается воронка
#  Обрабатываются все входящие сообщения в личных чатах (не считая Избранное)
@app.on_message(filters.private & ~filters.bot & ~filters.chat('me') & filters.incoming)
async def start(client: Client, message: Message):
    user_info = await is_user_exists(str(message.from_user.id))
    if not user_info:
        await add_user(str(message.from_user.id), message.from_user.username)
        logger.info(f'User {message.from_user.id} registered')

    await start_funnel(client, message.from_user.id, message.from_user.username, message.chat.id)


# Обработчик команды /users_today в чате Избранное (Saved Messaegs)
@app.on_message(filters.chat('me') & filters.command('users_today'))
async def get_users_today(client: Client, message: Message):
    today = datetime.utcnow().date()

    async with async_session_maker() as session:
        async with session.begin():
            query = select(func.count(User.id)).where(User.registration_date == today)
            result = await session.execute(query)
            users_today = result.all()[0][0]

    await client.send_message('me', f'За сегодняшний день зарегистрировалось {users_today} пользователей')


if __name__ == '__main__':
    app.run()
