from enum import Enum
from typing import List

from pydantic import BaseModel


class Role(Enum):
    SYSTEM: str = "system"
    USER: str = "user"
    ASSISTANT: str = "assistant"


class Message(BaseModel):
    role: Role
    content: str

    class Config:
        use_enum_values = True


def print_messages(messages: List[Message]) -> None:
    for message in messages:
        print(message.role)
        print(message.content)
        print("****")
