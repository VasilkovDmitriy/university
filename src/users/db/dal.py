from uuid import UUID

from sqlalchemy import select
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from users.db.models import User


class UserDAL:
    """Data Access Layer for operating user info"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_user(
        self, name: str, surname: str, email: str, hashed_password: str
    ) -> User:
        new_user = User(
            name=name,
            surname=surname,
            email=email,
            hashed_password=hashed_password,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user

    async def delete_user(self, user_id: UUID) -> UUID | None:
        query = (
            update(User)
            .where(User.id == user_id, bool(User.is_active))
            .values(is_active=False)
            .returning(User.id)
        )

        res = await self.db_session.execute(query)
        return res.scalar()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        query = select(User).where(User.id == user_id)

        res = await self.db_session.execute(query)
        return res.scalar()

    async def get_user_by_email(self, email: str) -> User | None:
        query = select(User).where(User.email == email)

        res = await self.db_session.execute(query)
        return res.scalar()

    async def update_user(self, user_id: UUID, **kwargs) -> UUID | None:
        query = (
            update(User)
            .where(User.id == user_id, bool(User.is_active))
            .values(**kwargs)
            .returning(User.id)
        )

        res = await self.db_session.execute(query)
        return res.scalar()
