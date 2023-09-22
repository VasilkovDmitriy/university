from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.actions.user import create_new_user_action, delete_user_action
from api.schemas import DeleteUserResponse, ShowUser, UserCreate
from db.session import get_db


user_router = APIRouter()


@user_router.post("/")
async def create_user(body: UserCreate, session: AsyncSession = Depends(get_db)) -> ShowUser:
    """User create handler."""

    return await create_new_user_action(body, session)


@user_router.delete("/{user_id}", response_model=DeleteUserResponse)
async def delete_user(user_id: UUID, session: AsyncSession = Depends(get_db)) -> DeleteUserResponse:
    deleted_user_id = await delete_user_action(user_id, session)

    if deleted_user_id is None:
        raise HTTPException(status_code=404, detail=f"User with id {user_id} not found.")

    return DeleteUserResponse(deleted_user_id=deleted_user_id)
