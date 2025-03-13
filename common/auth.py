from dataclasses import dataclass
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from enum import StrEnum
from config import get_settings

# JWT로 만든 액세스 토큰을 생성하고, 생성된 JWT를 다시 복호화하는 함수를 만든다.

settings = get_settings()

SECRET_KEY = settings.jwt_secret
ALGORITHM = "HS256"

# 권한 역할 구분
class Role(StrEnum):
    ADMIN = "ADMIN"
    USER = "USER"

async def create_access_token(
    payload: dict,
    role: Role,
    expires_delta: timedelta = timedelta(hours=6),
):
    expire = datetime.utcnow() + expires_delta 
    payload.update(
        {
            "role": role,
            "exp": expire       # 토큰 만료시간
        }
    )            
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

async def decode_access_token(token: str):
    try:
        # 토큰을 보안 키와 암호화 알고리즘으로 복호화
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])    
    except JWTError:
        # 암호화 키로 만들어진 키가 아니라면 에러 발생
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    
# tokenUrl은 앞서 만든 토큰을 발급하는 엔드포인트가 할당돼 있다.   
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# 토큰의 페이로드에 있는 정보를 담을 데이터 클래스
@dataclass
class CurrentUser:
    id: str
    role: Role

    def __str__(self):
        return f"{self.id}({self.role})"

# oauth2_scheme을 통해 얻은 토큰을 복호화한 페이로드에서 현재 유저의 정보를 구한다.
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    payload = await decode_access_token(token)

    user_id = payload.get("user_id")
    role = payload.get("role")
    # 페이로드에 필요한 정보가 없거나, 역할이 일반 유저의 역할이 아닐 경우
    if not user_id or not role or role != Role.USER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
    return CurrentUser(user_id, Role(role))

# def get_admin_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     payload = decode_access_token(token)

#     role = payload.get("role")
#     if not role or role != Role.ADMIN:
#         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    
#     return CurrentUser("ADMIN_USER_ID", role)
