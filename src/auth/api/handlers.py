from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from auth.api.schemas import CurrentUser
from auth.api.schemas import Token
from auth.services.get_current_user import get_current_user
from auth.usecases.login_for_access_token import LoginForAccessToken
from common.exceptions import Unauthorized
from db.session import get_db
from users.db.models import User


auth_router = APIRouter()


@auth_router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_db),
):
    try:
        login_for_access_token = LoginForAccessToken(db_session=session)
        access_token = await login_for_access_token(
            form_data.username, form_data.password
        )
        token = Token(access_token=access_token, token_type="bearer")
    except Unauthorized:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token


@auth_router.get("/test_auth_endpoint")
async def sample_endpoint_under_jwt(
    current_user: User = Depends(get_current_user),
) -> CurrentUser:
    return CurrentUser(
        id=current_user.id,
        name=current_user.name,
        surname=current_user.surname,
        email=current_user.email,
    )
