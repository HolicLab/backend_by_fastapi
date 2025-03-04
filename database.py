from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings

settings = get_settings()

SQLALCHEMY_DATABASE_URL = (
    # mysql+mysqldb로 연결, 데이터베이스의 유저 이름과 패스워드, 데이터베이스 스키마 이름
    "mysql+pymysql://"
    f"{settings.database_username}:{settings.database_password}"
    f"@mysql-docker:3306/{settings.database_name}"
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 데이터베이스 세션이 생성, 옵션으로 autocommit을 False로 해 별도의 커밋 명령이 없으면 커밋이 자동으로 실행되지 않음
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def create_tables():
    Base.metadata.create_all(bind=engine)

def create_trigger():
     with engine.connect() as connection:
        connection.execute(
            text("""
            DROP TRIGGER IF EXISTS update_study_session_subject;
            """)
        )
        connection.execute(
            text("""
            CREATE TRIGGER update_study_session_subject
            AFTER UPDATE ON subject
            FOR EACH ROW
            BEGIN
                IF NEW.subject_name <> OLD.subject_name THEN
                    UPDATE study_session
                    SET subject = NEW.subject_name
                    WHERE subject_id = OLD.id;
                END IF;
            END;
            """)
        )

def init_db():
    create_tables()
    create_trigger()