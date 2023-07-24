from enum import Enum

from pydantic import BaseModel


class Role(Enum):
    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"


class Message(BaseModel):
    role: Role
    content: str

    class Config:
        use_enum_values = True
