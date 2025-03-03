from dependency_injector import containers, providers

from user.application.user_service import UserService
# from note.application.note_service import NoteService

from user.infra.repository.user_repo import UserRepository
# from note.infra.repository.note_repo import NoteRepository

from study.infra.repository.study_repo import StudyRepository
from study.application.study_service import StudyService

from fastapi import BackgroundTasks
from user.application.email_service import EmailService

class Container(containers.DeclarativeContainer):
    # wiring_config = containers.WiringConfiguration(
    #     # 의존성을 사용할 모듈을 선언한다.
    #     packages=["user", "note", "study"],
    # )

    # 의존성을 제공할 모듈을 팩토리에 등록한다.
    user_repo = providers.Factory(UserRepository)
    # UserService 생성자로 전달될 user_repo 객체 역시 컨테이너에 있는 팩토리로 선언한다.
    user_service = providers.Factory(UserService, user_repo=user_repo)

    # note_repo = providers.Factory(NoteRepository)
    # note_service = providers.Factory(NoteService, note_repo=note_repo)

    study_repo = providers.Factory(StudyRepository)
    study_service = providers.Factory(StudyService, study_repo=study_repo)

    email_service = providers.Factory(EmailService)
    user_service = providers.Factory(
        UserService,
        user_repo=user_repo,
        email_service=email_service
    )