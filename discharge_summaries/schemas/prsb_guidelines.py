from pydantic import BaseModel


class Element(BaseModel):
    name: str
    description: str


class RecordEntry(BaseModel):
    name: str
    description: str
    elements: list[Element]


class Section(BaseModel):
    name: str
    description: str
    elements: list[Element] | RecordEntry
