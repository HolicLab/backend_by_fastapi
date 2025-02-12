from dataclasses import dataclass
from datetime import datetime

# @dataclass(데코레이터)를 이용해 생성자, 함수들을 자동으로 생성
@dataclass
class User:
    id: str
    name: str
    email: str
    password: str
    memo: str | None
    created_at: datetime
    updated_at: datetime