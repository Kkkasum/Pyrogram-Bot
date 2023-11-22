from datetime import datetime
from sqlalchemy import Column, Integer, String, Date

from src.database.database import Base


# Меодль существуещей таблицы user в базе данных (PostgreSQL)
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)
    username = Column(String, nullable=False)
    registration_date = Column(Date, default=datetime.utcnow().date())
