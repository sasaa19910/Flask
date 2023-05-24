import pydantic
from typing import Optional, Type


class CreateUser(pydantic.BaseModel):
    username: Optional[str]
    description: Optional[str]
    title: Optional[str]


class PatchUser(pydantic.BaseModel):
    username: Optional[str]
    description: Optional[str]
    title: Optional[str]


VALIDATION_CLASS = Type[CreateUser] | Type[PatchUser]