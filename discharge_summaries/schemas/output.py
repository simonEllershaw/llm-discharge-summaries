from pydantic import BaseModel


class Paragraph(BaseModel):
    text: str
    heading: str
    evidence: list[str] = []
