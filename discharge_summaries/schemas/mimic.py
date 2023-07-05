import re

from pydantic import BaseModel, validator


class Note(BaseModel):
    text: str
    datetime: str
    category: str
    description: str

    def __lt__(self, other: "Note") -> bool:
        return self.datetime < other.datetime


class DischargeSummary(Note):
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

    @property
    def bhc(self) -> str:
        start_pattern = r"\nBrief Hospital Course:\n"
        end_pattern = r"\nMedications on Admission:\n"
        match = re.search(f"{start_pattern}(.*?){end_pattern}", self.text, re.DOTALL)
        if not match:
            return ""
        return match.group(1)

    @property
    def bhc_sections(self) -> list[str]:
        return re.split("\n\n", self.bhc)

    @property
    def prefixes(self) -> list[str]:
        return [
            re.split(":|-", section, maxsplit=1)[0] for section in self.bhc_sections[1:]
        ]


class Record(BaseModel):
    physician_notes: list[Note]
    discharge_summary: DischargeSummary
    hadm_id: int
    subject_id: int
