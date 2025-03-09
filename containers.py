from dependency_injector import containers, providers

from user.application.user_service import UserService

from user.infra.repository.user_repo import UserRepository

from study.infra.repository.study_repo import StudyRepository
from study.application.study_service import StudyService

from fastapi import BackgroundTasks
from user.application.email_service import EmailService

import redis.asyncio as redis
from config import get_settings
from utils.crypto import Crypto

class Container(containers.DeclarativeContainer):
    settings = get_settings()
    # wiring_config = containers.WiringConfiguration(
    #     # 의존성을 사용할 모듈을 선언한다.
    #     packages=["user", "note", "study"],
    # )

    redis_client = providers.Singleton( # redis 관련 코드 추가.
        redis.Redis,
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password
    )

    crypto = providers.Factory(Crypto)

    # 의존성을 제공할 모듈을 팩토리에 등록한다.
    user_repo = providers.Factory(UserRepository)
    # UserService 생성자로 전달될 user_repo 객체 역시 컨테이너에 있는 팩토리로 선언한다.
    user_service = providers.Factory(UserService, user_repo=user_repo)

    study_repo = providers.Factory(StudyRepository)
    study_service = providers.Factory(StudyService, study_repo=study_repo)

    email_service = providers.Factory(EmailService)
    user_service = providers.Factory(
        UserService,
        user_repo=user_repo,
        email_service=email_service,
        crypto=crypto,
        redis=redis_client,
    )