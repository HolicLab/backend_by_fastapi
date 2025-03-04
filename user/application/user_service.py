from fastapi import BackgroundTasks, HTTPException, Depends, status
from ulid import ULID
from datetime import datetime
from user.domain.user import User
from user.domain.repository.user_repo import IUserRepository
from user.application.email_service import EmailService
from user.application.send_welcome_email_task import SendWelcomeEmailTask
from utils.crypto import Crypto
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from common.auth import Role, create_access_token
import pytz

korea_timezone = pytz.timezone('Asia/Seoul')

class UserService:
    # @inject 데커레이터를 명시해 주입받은 객체를 사용한다고 선언한다.
    # 컨테이너에 직접 user_repo 팩토리를 선언해두었기 때문에 타입 선언만으로도 
    # UserService가 생성될 때 팩토리를 수행한 객체가 주입된다.
    @inject
    def __init__(self, user_repo: IUserRepository, email_service: EmailService):
        self.user_repo = user_repo
        self.ulid = ULID()
        self.crypto = Crypto()
        self.email_service = email_service
        

    def create_user(
        self, 
        # background_tasks: BackgroundTasks, 
        name: str, 
        email: str, 
        password: str, 
        memo: str | None = None
    ):
        now_korea = datetime.now(korea_timezone)
        _user = None        # 데이터베이스에서 찾은 유저 변수

        try:
            _user = self.user_repo.find_by_email(email)
        except HTTPException as e:
            if e.status_code != 422:
                raise e
        # 가입한 유저일 경우 422에러를 발생시킨다.
        if _user:
            raise HTTPException(status_code=422)

        user: User = User(
            id=self.ulid.generate(),
            name=name,
            email=email,
            password=self.crypto.encrypt(password),
            memo=memo,
            created_at=now_korea,
            updated_at=now_korea,
        )
        self.user_repo.save(user)

        # SendWelcomeEmailTask().run(user.email)
        
        # background_tasks.add_task(
        #     self.email_service.send_email, user.email
        # )
        return user
    
    def update_user(
            self,
            user_id: str,
            name: str | None = None,
            password: str | None = None,
    ):
        now_korea = datetime.now(korea_timezone)
        user = self.user_repo.find_by_id(user_id)

        if name:
            user.name = name
        if password:
            user.password = self.crypto.encrypt(password)
        user.updated_at = now_korea

        self.user_repo.update(user)

        return user
    
    def get_users(self, page: int, items_per_page: int) -> tuple[int, list[User]]:
        users = self.user_repo.get_users(page, items_per_page)
        
        return users
    
    def delete_user(self, user_id: str):
        self.user_repo.delete(user_id)

    def login(self, email: str, password: str):
        # 가입한 유저를 찾는다.
        user = self.user_repo.find_by_email(email)

        # 전달받은 패스워드와 데이터베이스에 저장된 패스워드와 비교해 유효성 검증
        if not self.crypto.verify(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        
        access_token = create_access_token(
            payload={"user_id": user.id},
            role=Role.USER,
        )

        return access_token
