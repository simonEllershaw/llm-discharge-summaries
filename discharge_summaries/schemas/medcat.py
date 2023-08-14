from typing import List

import spacy
from medcat.cat import CAT
from pydantic import BaseModel


class MedCATSpan(BaseModel):
    start: int
    end: int
    text: str
    cui: str
    name: str
    type_ids: List[str]
    context: str = ""
    meta_anns: dict = {}
    datetime: str = ""

    @classmethod
    def from_spacy_span(
        cls, span: spacy.tokens.Span, cat: CAT, context=None, datetime=""
    ):
        cui = str(span._.cui)
        return cls(
            start=span.start_char,
            end=span.end_char,
            text=span.text,
            cui=cui,
            name=cat.cdb.get_name(cui),
            type_ids=list(cat.cdb.cui2type_ids.get(cui, "")),
            context=context if context else "",
            meta_anns=span._.meta_anns if span._.meta_anns else {},
            datetime=datetime,
        )
