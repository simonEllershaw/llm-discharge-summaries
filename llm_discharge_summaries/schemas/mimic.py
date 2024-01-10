from typing import List

from pydantic import BaseModel


class Note(BaseModel):
    text: str
    datetime: str
    category: str
    description: str

    def __lt__(self, other: "Note") -> bool:
        return self.datetime < other.datetime


class Record(BaseModel):
    physician_notes: List[Note]
    hadm_id: int
    subject_id: int


class ProblemSection(BaseModel):
    heading: str
    text: str

    class Config:
        frozen = True


class BHC(BaseModel):
    hadm_id: int
    assessment_and_plan: str
    problem_sections: List[ProblemSection]
    full_text: str


class PhysicianNote(BaseModel):
    hadm_id: int
    title: str
    timestamp: str
    text: str
