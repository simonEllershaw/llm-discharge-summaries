from typing import List

from pydantic import BaseModel


class Paragraph(BaseModel):
    text: str
    heading: str
    evidence: List[str] = []
