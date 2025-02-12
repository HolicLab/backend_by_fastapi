from fastapi import BackgroundTasks, APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated
from dependency_injector.wiring import inject, Provide
from containers import Container
from datetime import datetime
from common.auth import CurrentUser, get_current_user
# from common.auth import get_admin_user

from user.application.user_service import UserService


router = APIRouter(prefix="/users")

# 파이단틱 모델 선언(파이단틱의 BaseModel을 상속받는다.)
class CreateUserBody(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)
    password: str = Field(min_length=8, max_length=32)

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

@router.post("", status_code=201)     # 201 Created : 요청이 성공적
@inject
def create_user(
    user: CreateUserBody,
    # background_tasks: BackgroundTasks,
    # 의존성 주입 : UserService객체를 생성하지 않고 UserService 객체를 전달받도록 할 수 있다.
    user_service: UserService = Depends(Provide[Container.user_service]),
    # user_service: UserService = Depends(Provide["user_service"])
) -> UserResponse:
    created_user = user_service.create_user(
        # background_tasks=background_tasks,
        name=user.name,
        email=user.email,
        password=user.password
    )

    return created_user

# 파이단틱 모델
class UpdateUserBody(BaseModel):
    name: str | None = Field(min_length=2, max_length=32, default=None)
    password: str | None = Field(min_length=8, max_length=32, default=None)

@router.put("", response_model=UserResponse)
@inject
def update_user(
    # get_current_user의 수행 결과를 주입받는다. 토큰에 들어있는 유저의 ID를 사용
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body: UpdateUserBody,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    user = user_service.update_user(
        user_id=current_user.id,
        name=body.name,
        password=body.password,
    )

    return user

class GetUsersResponse(BaseModel):
    total_count:int
    page: int
    users: list[UserResponse]

@router.get("")
@inject
def get_users(
    page: int = 1,
    items_per_page: int = 10,
    # get_admin_user 함수의 결과를 주입해 어드민용 토큰을 검사한다.
    # current_user: CurrentUser = Depends(get_admin_user),
    user_service: UserService = Depends(Provide[Container.user_service])
) -> GetUsersResponse:
    total_count, users = user_service.get_users(page, items_per_page)

    return {
        "total_count": total_count,
        "page": page,
        "users": users,
    }

# 204 No Content : 요청이 성공했으나 클라이언트가 현재 페이지에서 벗어나지 않아도 된다는 것을 나타냄
@router.delete("", status_code=204)
@inject
def delete_user(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    user_service.delete_user(current_user.id)

@router.post("/login")
@inject
def login(
    # FastAPI가 제공하는 OAuth2PasswordRequestForm 클래스를 이용해 유저의 아이디와 패스워드를 전달받는다.
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    access_token = user_service.login(
        email=form_data.username,
        password=form_data.password,
    )

    return {"access_token": access_token, "token_type": "bearer"}

