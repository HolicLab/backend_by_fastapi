import redis.asyncio as redis
from fastapi import BackgroundTasks, HTTPException, Depends, status
from ulid import ULID
from datetime import datetime, timedelta, timezone
from user.domain.user import User
from user.domain.repository.user_repo import IUserRepository
from user.application.email_service import EmailService
from user.application.send_welcome_email_task import SendWelcomeEmailTask
from utils.crypto import Crypto
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from common.auth import Role, create_access_token
import pytz
import secrets

korea_timezone = pytz.timezone('Asia/Seoul')

class UserService:
    # @inject 데커레이터를 명시해 주입받은 객체를 사용한다고 선언한다.
    # 컨테이너에 직접 user_repo 팩토리를 선언해두었기 때문에 타입 선언만으로도 
    # UserService가 생성될 때 팩토리를 수행한 객체가 주입된다.
    @inject
    def __init__(self, user_repo: IUserRepository, email_service: EmailService, crypto: Crypto, redis: redis.Redis):
        self.user_repo = user_repo
        self.ulid = ULID()
        self.crypto = Crypto()
        self.email_service = email_service
        self.redis = redis

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
    
    # PIN 생성, 저장 (hashed), 유효 시간 설정
    async def create_pin(self, user_id: str) -> tuple[str, datetime]:
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        expires_at = datetime.now(korea_timezone) + timedelta(minutes=2) 

        while True:
            pin = "".join([str(secrets.randbelow(10)) for _ in range(6)])
            set_result = await self.redis.setnx(pin, f"{user_id}:{expires_at.timestamp()}")
            if set_result:
                await self.redis.expire(pin, 600)
                break

        # 디버깅 출력
        data = await self.redis.get(pin)
        print(f"Raw data: {data}")  
        print(f"Decoded data: {data.decode('utf-8')}")  

        return (pin, expires_at)

    async def verify_pin_and_login(self, pin: str) -> str:
        """PIN 검증 (Redis), JWT 생성, 명시적 만료 시간 확인."""

        # Redis에서 PIN 정보 가져오기
        data = await self.redis.get(pin)  # user_id:expires_at (str)
        if not data:
            raise HTTPException(status_code=404, detail="PIN not found")

        # data(bytes)를 문자열로 디코딩
        data_str = data.decode("utf-8")
        print(f"utf-8 : {data_str}")
        
        if ":" not in data_str:
            await self.redis.delete(pin)  # 잘못된 형식의 데이터 삭제
            raise HTTPException(status_code=400, detail="Invalid PIN data format.")

        # 🔹 `split(":", 1)` 사용하여 정확하게 분리
        try:
            user_id, expires_at_str = data_str.split(":", 1)  
            expires_at = datetime.fromtimestamp(float(expires_at_str), korea_timezone)  # Unix timestamp 변환
        except (ValueError, IndexError) as e:
            await self.redis.delete(pin)  # 잘못된 데이터 삭제
            raise HTTPException(status_code=400, detail=f"Invalid expiration time format: {str(e)}")

        # 현재 시간이 만료 시간을 초과했는지 확인
        if datetime.now(korea_timezone) > expires_at:
            await self.redis.delete(pin)  # 만료된 PIN 삭제
            raise HTTPException(status_code=410, detail="PIN expired")

        # PIN 정보 삭제 (일회용)
        await self.redis.delete(pin)

        access_token = create_access_token(payload={"user_id": user_id}, role=Role.USER)
        return access_token

