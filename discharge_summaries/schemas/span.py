from pydantic import BaseModel


class Span(BaseModel):
    start: int
    end: int
    text: str
    label: str
