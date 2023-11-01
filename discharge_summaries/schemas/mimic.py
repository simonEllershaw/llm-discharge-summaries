from typing import List

from pydantic import BaseModel, validator

from discharge_summaries.schemas.output import Paragraph


class Note(BaseModel):
    text: str
    datetime: str
    category: str
    description: str

    def __lt__(self, other: "Note") -> bool:
        return self.datetime < other.datetime


class DischargeSummary(Note):
    bhc: str
    bhc_paragraphs: List[Paragraph]

    @validator("category")
    def category_must_be_discharge_summary(cls, v):
        if v != "Discharge summary":
            raise ValueError("must be Discharge summary")
        return v

    @validator("description")
    def description_must_be_report(cls, v):
        if v != "Report":
            raise ValueError("must be Report")
        return v


class Record(BaseModel):
    physician_notes: List[Note]
    discharge_summary: DischargeSummary
    hadm_id: int
    subject_id: int


class ProblemSection(BaseModel):
    heading: str
    text: str


class BHC(BaseModel):
    hadm_id: int
    full_text: str
    assessment_and_plan: str
    problem_sections: List[ProblemSection]
