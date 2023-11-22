from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from src.config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME


DB_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'  # asyncpg
Base = declarative_base()

engine = create_async_engine(DB_URL, poolclass=NullPool)
async_session_maker = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
