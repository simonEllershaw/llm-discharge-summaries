from typing import List, Set

from spacy.language import Language
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc, Span
from tqdm import tqdm

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
        parent_cuis: Set[int],
        snomed_lookup: SnomedLookup,
        spacy_lemma_pipeline: Language,
        keep_child_cuis=False,
    ):
        self._nlp = spacy_lemma_pipeline

        cui_to_synonyms_lower = {}
        for parent_cui in parent_cuis:
            parent_synonyms = {
                synonym.lower()
                for synonym in snomed_lookup.cui_to_synonyms.get(parent_cui, set())
            }
            if not parent_synonyms:
                raise ValueError(f"Parent CUI {parent_cui} has no synonyms")
            cui_to_synonyms_lower[parent_cui] = parent_synonyms

            for child_cui in snomed_lookup.get_child_cuis(parent_cui):
                child_synonyms = {
                    synonym.lower()
                    for synonym in snomed_lookup.cui_to_synonyms.get(child_cui, set())
                }
                if keep_child_cuis:
                    cui_to_synonyms_lower[child_cui] = child_synonyms
                else:
                    cui_to_synonyms_lower[parent_cui].union(child_synonyms)

        self._phrase_matcher = PhraseMatcher(self._nlp.vocab, "LEMMA")
        for cui, synonyms_lower in tqdm(cui_to_synonyms_lower.items()):
            self._phrase_matcher.add(str(cui), list(self._nlp.pipe(synonyms_lower)))

    def _get_cuis_in_doc(self, doc: Doc) -> List[int]:
        snomed_matches = self._phrase_matcher(doc, as_spans=True)
        filtered_snomed_matches = _filter_out_subspans(snomed_matches)
        snomed_cuis = [int(span.label_) for span in filtered_snomed_matches]
        if not snomed_cuis and "/" in doc.text:
            return self(doc.text.replace("/", " "))
        return snomed_cuis

    def __call__(self, text: str) -> List[int]:
        doc = self._nlp(text.lower())
        return self._get_cuis_in_doc(doc)

    def pipe(self, texts: List[str]) -> List[List[int]]:
        texts_lower = [text.lower() for text in texts]
        return [self._get_cuis_in_doc(doc) for doc in self._nlp.pipe(texts_lower)]
