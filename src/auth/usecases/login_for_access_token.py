from typing import final

import attr
from sqlalchemy.ext.asyncio import AsyncSession

from auth.services.create_access_token import create_access_token
from auth.services.hashing import Hasher
from common.exceptions import Unauthorized
from users.db.dal import UserDAL


@final
@attr.dataclass(slots=True, frozen=True)
class LoginForAccessToken:
    db_session: AsyncSession

    async def __call__(self, user_email: str, password: str) -> str:
        async with self.db_session.begin():
            user_dal = UserDAL(self.db_session)

            user = await user_dal.get_user_by_email(user_email)

        if not user:
            raise Unauthorized

        if not Hasher.verify_password(password, user.hashed_password):
            raise Unauthorized

        access_token = create_access_token({"sub": user_email})
        return access_token
