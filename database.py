from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings

settings = get_settings()

SQLALCHEMY_DATABASE_URL = (
    # mysql+mysqldb로 연결, 데이터베이스의 유저 이름과 패스워드, 데이터베이스 스키마 이름
    "mysql+aiomysql://"
    f"{settings.database_username}:{settings.database_password}"
    f"@mysql-docker:3306/{settings.database_name}"
)
async_engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True, future=True)

# 데이터베이스 세션이 생성, 옵션으로 autocommit을 False로 해 별도의 커밋 명령이 없으면 커밋이 자동으로 실행되지 않음
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def init_db():
    await create_tables()