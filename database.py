from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings

settings = get_settings()

SQLALCHEMY_DATABASE_URL = (
    # mysql+mysqldb로 연결, 데이터베이스의 유저 이름과 패스워드, 데이터베이스 스키마 이름
    "mysql+pymysql://"
    f"{settings.database_username}:{settings.database_password}"
    f"@{settings.docker_database}"
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 데이터베이스 세션이 생성, 옵션으로 autocommit을 False로 해 별도의 커밋 명령이 없으면 커밋이 자동으로 실행되지 않음
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
