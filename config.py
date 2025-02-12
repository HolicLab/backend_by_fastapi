from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

# 파이단틱 모델이면서 환경변수를 다루는 클래스
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )

    database_username: str
    database_password: str
    jwt_secret: str
    email_password: str
    celery_broker_url: str
    celery_backend_url: str

# 페이지 교체 알고리즘중 하나인 lru알고리즘으로 이미 구한 값이 있다면 그 값을 반환한다.
@lru_cache
def get_settings():
    return Settings()

