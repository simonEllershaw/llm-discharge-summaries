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
    context: str
    meta_anns: dict

    @classmethod
    def from_spacy_span(
        cls, span: spacy.tokens.Span, cat: CAT, context_length: int = 20
    ):
        start = span.start_char
        end = span.end_char
        cui = str(span._.cui)
        name = cat.cdb.get_name(cui)
        type_ids = list(cat.cdb.cui2type_ids.get(cui, ""))
        text = span.text
        meta_anns = span._.meta_anns if hasattr(span._, "meta_anns") else {}
        context = " ".join(
            [
                token.text
                for token in span.doc[
                    max(0, span.start - context_length) : min(
                        len(span.doc), span.end + context_length
                    )
                ]
            ]
        )
        return cls(
            start=start,
            end=end,
            text=text,
            cui=cui,
            name=name,
            type_ids=type_ids,
            context=context,
            meta_anns=meta_anns,
        )
