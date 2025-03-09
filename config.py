from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# 파이단틱 모델이면서 환경변수를 다루는 클래스
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    database_username: str
    database_password: str
    database_host: str       # 호스트
    database_name: str       # 데이터베이스 이름
    jwt_secret: str
    email_password: str
    celery_broker_url: str
    celery_backend_url: str
    redis_host: str = Field(..., env="REDIS_HOST") # 추가
    redis_port: int = Field(..., env="REDIS_PORT") # 추가
    redis_db: int = Field(0, env="REDIS_DB")   # 추가, 기본값 0
    redis_password: str | None = Field(None, env="REDIS_PASSWORD")

# 페이지 교체 알고리즘중 하나인 lru알고리즘으로 이미 구한 값이 있다면 그 값을 반환한다.
@lru_cache
def get_settings():
    return Settings()

