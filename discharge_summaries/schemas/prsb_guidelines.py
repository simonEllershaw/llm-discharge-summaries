from pydantic import BaseModel


class Element(BaseModel):
    name: str
    description: str
    values: str
    snomed_codes: list[str] | None


class RecordEntry(BaseModel):
    name: str
    description: str
    elements: list[Element]


class Section(BaseModel):
    name: str
    description: str
    elements: list[Element] | RecordEntry
    restrict_to_last_note: bool
