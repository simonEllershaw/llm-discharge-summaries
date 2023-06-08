from enum import Enum

from pydantic import BaseModel


class Role(Enum):
    SYSTEM: str = "system"
    USER: str = "user"
    ASSISTANT: str = "assistant"


class Message(BaseModel):
    role: Role
    content: str


def print_messages(messages: list[Message]) -> None:
    for message in messages:
        print(message.role)
        print(message.content)
        print("****")
