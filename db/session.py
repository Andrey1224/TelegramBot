# This file handles database connection setup and session management
# it defines engine, AsyncSession, and PRAGMA settings for foreign keys

import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import event

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bot.db")

# Context: this function is used within the application to create database engine
# with proper async support and SQLite configuration
# 1. Создаём асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Context: this function is used within database operations to enable foreign keys
# 2. Включаем проверку внешних ключей в SQLite
@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragma(dbapi_conn, conn_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Context: this function is used within database operations to get async session
# 3. Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Context: this function is used within handlers to get database session
# 4. Утилита для использования в хендлерах
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session