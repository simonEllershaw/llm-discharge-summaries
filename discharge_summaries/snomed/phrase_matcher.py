from typing import List

from spacy.language import Language
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc, Span

from .lookup import SnomedLookup


def _is_sub_span(sub_span: Span, span: Span) -> bool:
    return span.start <= sub_span.start and span.end >= sub_span.end


def _filter_out_subspans(spans: List[Span]) -> List[Span]:
    sorted_spans = sorted(spans, key=len, reverse=True)
    full_spans: List[Span] = list()
    for span in sorted_spans:
        # Check if the span overlaps with any previously confirmed full spans
        if all(not _is_sub_span(span, full_span) for full_span in full_spans):
            full_spans.append(span)
    return sorted(full_spans, key=lambda span: span.start)


class SnomedPhraseMatcher:
    def __init__(
        self,
        spacy_lemma_pipeline: Language,
        use_child_cui_label=False,
    ):
        self._nlp = spacy_lemma_pipeline
        self._phrase_matcher = PhraseMatcher(self._nlp.vocab, "LEMMA")
        self._use_child_cui_label = use_child_cui_label

    def add_parent_cui(self, parent_cui: int, snomed_lookup: SnomedLookup):
        cui_to_synonyms = {}
        cui_to_synonyms[parent_cui] = snomed_lookup.cui_to_synonyms[parent_cui]

        for child_cui in snomed_lookup.get_child_cuis(parent_cui):
            child_synonyms = snomed_lookup.cui_to_synonyms[parent_cui]
            if self._use_child_cui_label:
                cui_to_synonyms[child_cui] = child_synonyms
            else:
                cui_to_synonyms[parent_cui].union(child_synonyms)
        cui_to_synonyms = {
            cui: {synonym.lower() for synonym in synonyms}
            for cui, synonyms in cui_to_synonyms.items()
        }

        for cui, synonyms_lower in cui_to_synonyms.items():
            self._phrase_matcher.add(str(cui), list(self._nlp.pipe(synonyms_lower)))

    def _get_cuis_in_doc(self, doc: Doc) -> List[int]:
        snomed_matches = self._phrase_matcher(doc, as_spans=True)
        filtered_snomed_matches = _filter_out_subspans(snomed_matches)
        snomed_cuis = [int(span.label_) for span in filtered_snomed_matches]
        # Catch edge cases such as anxiety/depression
        if not snomed_cuis and "/" in doc.text:
            return self(doc.text.replace("/", " "))
        return snomed_cuis

    def __call__(self, text: str) -> List[int]:
        doc = self._nlp(text.lower())
        return self._get_cuis_in_doc(doc)

    def pipe(self, texts: List[str]) -> List[List[int]]:
        docs = self._nlp.pipe([text.lower() for text in texts])
        return [self._get_cuis_in_doc(doc) for doc in docs]
