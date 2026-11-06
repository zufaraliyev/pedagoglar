import os
import logging
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

load_dotenv()
logger = logging.getLogger("pedstart.db")

# 1. MySQL konfiguratsiya parametrlarini o'qish
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "pedstart_db")

# Standart MySQL URL (aiomysql drayveri orqali)
default_mysql_url = f"mysql+aiomysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
DATABASE_URL = os.getenv("DATABASE_URL", default_mysql_url)

# Agar foydalanuvchi "mysql://" formatida yozgan bo'lsa, uni "mysql+aiomysql://" ga o'giramiz
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+aiomysql://", 1)


def ensure_mysql_database_exists():
    """
    Agar MySQL serverida 'pedstart_db' bazasi hali yaratilmagan bo'lsa,
    uni utf8mb4 kodi bilan avtomatik yaratadi (Unknown database xatosini oldini olish uchun).
    """
    try:
        import pymysql
        conn = pymysql.connect(
            host=DB_HOST,
            port=int(DB_PORT),
            user=DB_USER,
            password=DB_PASSWORD,
            charset="utf8mb4"
        )
        with conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.commit()
        conn.close()
        logger.info(f"MySQL bazasi '{DB_NAME}' tekshirildi/yaratildi.")
    except Exception as e:
        logger.warning(
            f"MySQL bazasini tekshirishda ogohlantirish: {e}. "
            "Iltimos, MySQL xizmati (masalan, XAMPP / MySQL Server) yoqilganini tekshiring."
        )


# MySQL uchun engine sozlamalari
# DIQQAT: pool_pre_ping=True aiomysql/asyncmy bilan TypeError: ping() missing 1 required positional argument: 'reconnect' xatosini chaqirishi mumkin.
# Shuning uchun pool_recycle=3600 yetarli va barqaror.
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_recycle=3600,
    connect_args={"charset": "utf8mb4"}
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    """FastAPI yo'llari uchun ma'lumotlar bazasi sessiyasi dependency'si"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
