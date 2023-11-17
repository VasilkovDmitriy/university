from fastapi import Depends
from jose import jwt
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.api.schemas import TokenData
from auth.settings import ALGORITHM
from auth.settings import oauth2_scheme
from auth.settings import SECRET_KEY
from common.exceptions import Unauthorized
from db.session import get_db
from users.db.dal import UserDAL
from users.db.models import User


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")

        if email is None:
            raise Unauthorized

        token_data = TokenData(email=email)
    except JWTError:
        raise Unauthorized

    user_dal = UserDAL(db_session)
    user = await user_dal.get_user_by_email(token_data.email)

    if user is None:
        raise Unauthorized

    return user
