import spacy
from medcat.cat import CAT
from pydantic import BaseModel


class MedCATSpan(BaseModel):
    start: int
    end: int
    text: str
    cui: str
    name: str
    type_ids: list[str]
    context: str = ""
    meta_anns: dict = {}

    @classmethod
    def from_spacy_span(cls, span: spacy.tokens.Span, cat: CAT, context=None):
        cui = str(span._.cui)
        return cls(
            start=span.start_char,
            end=span.end_char,
            text=span.text,
            cui=cui,
            name=cat.cdb.get_name(cui),
            type_ids=list(cat.cdb.cui2type_ids.get(cui, "")),
            context=context if context else "",
            meta_anns=span._.meta_anns if hasattr(span._, "meta_anns") else {},
        )
