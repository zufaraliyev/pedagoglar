import logging
import os

import pymysql
from dotenv import load_dotenv
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()
logger = logging.getLogger("pedtayyor.db")

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "pedtayyor_db")

default_mysql_url = (
    f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/"
    f"{DB_NAME}?charset=utf8mb4"
)
database_url = os.getenv("DATABASE_URL", default_mysql_url)

if database_url.startswith("mysql://"):
    database_url = database_url.replace("mysql://", "mysql+aiomysql://", 1)
elif database_url.startswith(("postgres://", "postgresql://")):
    database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

url = make_url(database_url)
connect_args = {}

if url.get_backend_name() == "postgresql":
    query = dict(url.query)
    sslmode = query.pop("sslmode", None)
    query.pop("channel_binding", None)
    url = url.set(query=query)
    if sslmode and sslmode != "disable":
        connect_args["ssl"] = "require"
elif url.get_backend_name() == "mysql":
    connect_args["charset"] = "utf8mb4"

DATABASE_URL = url.render_as_string(hide_password=False)


def ensure_mysql_database_exists():
    if url.get_backend_name() != "mysql":
        return

    try:
        connection = pymysql.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            charset="utf8mb4",
        )
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                )
            connection.commit()
        finally:
            connection.close()
        logger.info("MySQL bazasi '%s' tekshirildi/yaratildi.", DB_NAME)
    except Exception:
        logger.exception("MySQL bazasini tekshirishda xatolik yuz berdi.")
        raise


engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_recycle=3600,
    connect_args=connect_args,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
