from datetime import datetime
from datetime import timedelta

from jose import jwt

from auth.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from auth.settings import ALGORITHM
from auth.settings import SECRET_KEY


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    expires_delta = expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    expire = datetime.utcnow() + expires_delta

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
