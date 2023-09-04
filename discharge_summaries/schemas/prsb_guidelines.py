from typing import List

from pydantic import BaseModel


class Element(BaseModel):
    name: str
    description: str
    cardinality: str
    values: str


class Section(BaseModel):
    name: str
    description: str
    elements: List[Element]
