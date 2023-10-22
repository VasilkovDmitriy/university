from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.user import create_new_user_action
from api.actions.user import delete_user_action
from api.actions.user import get_user_by_email_action
from api.actions.user import get_user_by_id_action
from api.actions.user import update_user_action
from api.schemas import DeleteUserResponse
from api.schemas import ShowUser
from api.schemas import UpdatedUserRequest
from api.schemas import UpdatedUserResponse
from api.schemas import UserCreate
from db.session import get_db

user_router = APIRouter()


@user_router.post("/")
async def create_user(
    body: UserCreate, session: AsyncSession = Depends(get_db)
) -> ShowUser:
    """Create user handler."""

    if await get_user_by_email_action(body.email, session):
        raise HTTPException(
            status_code=409, detail="A user with this email already exists"
        )

    return await create_new_user_action(body, session)


@user_router.delete("/{user_id}")
async def delete_user(
    user_id: UUID, session: AsyncSession = Depends(get_db)
) -> DeleteUserResponse:
    """Delete user handler."""

    deleted_user_id = await delete_user_action(user_id, session)

    if deleted_user_id is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )

    return DeleteUserResponse(deleted_user_id=deleted_user_id)


@user_router.get("/{user_id}")
async def get_user(user_id: UUID, session: AsyncSession = Depends(get_db)) -> ShowUser:
    """Get user handler."""

    user = await get_user_by_id_action(user_id, session)

    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )

    return user


@user_router.patch("/{user_id}")
async def update_user(
    user_id: UUID, body: UpdatedUserRequest, session: AsyncSession = Depends(get_db)
) -> UpdatedUserResponse:
    if body.email and await get_user_by_email_action(body.email, session):
        raise HTTPException(
            status_code=409, detail="A user with this email already exists"
        )

    updated_user_params = body.dict(exclude_none=True)

    if updated_user_params == {}:
        raise HTTPException(
            status_code=422,
            detail="At least one parameter for user update info should be provided",
        )

    user = await get_user_by_id_action(user_id, session)

    if user is None:
        raise HTTPException(
            status_code=404, detail=f"User with id {user_id} not found."
        )

    updated_user_id = await update_user_action(user_id, updated_user_params, session)

    return UpdatedUserResponse(updated_user_id=updated_user_id)
