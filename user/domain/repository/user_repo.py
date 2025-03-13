# 도메인을 영속화하기 위해 인터페이스를 구현
# 이 모듈은 어느 계층에서나 사용할 수 있으며, 인프라 계층보다 고수준의 계층에서 사용할 때는 그 의존성이 역전돼 있음
from abc import ABCMeta, abstractmethod
from user.domain.user import User

# metaclass=ABCMeta를 사용하여 IUserRepository 클래스가 추상 클래스임을 선언
class IUserRepository(metaclass=ABCMeta):
    @abstractmethod
    async def save(self, user:User):
        raise NotImplementedError
    
    @abstractmethod
    async def find_by_email(self, email: str) -> User:
        """
        이메일로 유저를 검색한다.
        검색한 유저가 없을 경우 422 에러를 발생시킨다.
        """
        raise NotImplementedError

    @abstractmethod
    async def find_by_id(self, id: str) -> User:
        raise NotImplementedError
    
    @abstractmethod
    async def update(self, user: User):
        raise NotImplementedError
    
    @abstractmethod
    async def get_users(self, page: int, items_per_page: int) -> tuple[int, list[User]]:
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self, id: str):
        raise NotImplementedError
    
    