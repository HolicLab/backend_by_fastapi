from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.sql import func
from database import AsyncSessionLocal
from user.domain.repository.user_repo import IUserRepository
from user.domain.user import User as UserVO
from user.infra.db_models.user import User
from utils.db_utils import row_to_dict

class UserRepository(IUserRepository):
    async def save(self, user: UserVO):
        new_user = User(
            id=user.id,
            email=user.email,
            name=user.name,
            password=user.password,
            memo=user.memo,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

        async with AsyncSessionLocal() as db:
            try:
                db.add(new_user)
                await db.commit()
            except Exception as e:
                await db.rollback()
                raise e

    async def find_by_email(self, email: str) -> UserVO:
        async with AsyncSessionLocal() as db:
            query = select(User).where(User.email == email)
            result = await db.execute(query)
            user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=422, detail="User not found")
        
        return UserVO(**row_to_dict(user))
    
    async def find_by_id(self, id: str):
        async with AsyncSessionLocal() as db:
            query = select(User).where(User.id == id)
            result = await db.execute(query)
            user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=422, detail="User not found")
        
        return UserVO(**row_to_dict(user))

    async def update(self, user_vo: UserVO):
        async with AsyncSessionLocal() as db:
            query = select(User).where(User.id == user_vo.id)
            result = await db.execute(query)
            user = result.scalars().first()

            if not user:
                raise HTTPException(status_code=422, detail="User not found")
            
            user.name = user_vo.name
            user.password = user_vo.password
            
            await db.commit()

        return UserVO(**row_to_dict(user))
    
    async def get_users(self, page: int = 1, items_per_page: int = 10) -> tuple[int, list[UserVO]]:
        async with AsyncSessionLocal() as db:
            total_count_query = select(func.count()).select_from(User)
            total_count_result = await db.execute(total_count_query)
            total_count = total_count_result.scalar()

            query = (
                select(User)
                .offset((page -1) * items_per_page)
                .limit(items_per_page)
            )
            
            result = await db.execute(query)                     # 몇 개의 데이터를 건너뛸지를 계산
            users = result.scalars().all()    # limit로 페이지에 표시할 만큼만 조회한다.

        return total_count, [UserVO(**row_to_dict(user)) for user in users]
        
    async def delete(self, id: str):
        async with AsyncSessionLocal() as db:
            query = select(User).where(User.id == id)
            result = await db.execute(query)
            user = result.scalars().first()

            if not user:
                raise HTTPException(status_code=422, detail="User not found")
            
            await db.delete(user)
            await db.commit()