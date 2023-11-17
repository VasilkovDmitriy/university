import uuid

from pydantic import BaseModel
from pydantic import EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class CurrentUser(BaseModel):
    id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
