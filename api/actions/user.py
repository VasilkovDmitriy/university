from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas import ShowUser, UserCreate
from db.dal import UserDAL


async def create_new_user_action(body: UserCreate, session: AsyncSession) -> ShowUser:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.create_user(
            name=body.name,
            surname=body.surname,
            email=body.email,
        )
        return ShowUser(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_active=user.is_active,
        )


async def delete_user_action(user_id: UUID, session: AsyncSession) -> UUID | None:
    async with session.begin():
        user_dal = UserDAL(session)
        deleted_user_id = await user_dal.delete_user(user_id)
        return deleted_user_id


async def get_user_by_id_action(user_id: UUID, session: AsyncSession) -> ShowUser | None:
    async with session.begin():
        user_dal = UserDAL(session)
        user = await user_dal.get_user_by_id(user_id)

        if not user:
            return None

        return ShowUser(
            user_id=user.user_id,
            name=user.name,
            surname=user.surname,
            email=user.email,
            is_active=user.is_active,
        )


async def get_user_by_email_action(email: str, session: AsyncSession) -> ShowUser | None:
    async with session.begin():
        user_dal = UserDAL(session)

        if user := await user_dal.get_user_by_email(email):
            return ShowUser(
                user_id=user.user_id,
                name=user.name,
                surname=user.surname,
                email=user.email,
                is_active=user.is_active,
            )


async def update_user_action(user_id: UUID, updated_user_params: dict, session: AsyncSession) -> UUID | None:
    async with session.begin():
        user_dal = UserDAL(session)
        updated_user_id = await user_dal.update_user(user_id, **updated_user_params)
        return updated_user_id
