from typing import Iterable, List

import numpy as np
from spacy.language import Language
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc, Span
from spacy.util import filter_spans

from .lookup import SnomedLookup


@Language.component("lower_case_lemmas")
def lower_case_lemmas(doc: Doc) -> Doc:
    for token in doc:
        if token.is_upper:
            token.lemma_ = token.lemma_.upper()
        else:
            token.lemma_ = token.lemma_.lower()
    return doc


class SnomedPhraseMatcher:
    def __init__(
        self,
        spacy_lemma_pipeline: Language,
        use_child_cui_label=False,
        min_phrase_length=2,
    ):
        self._nlp = spacy_lemma_pipeline
        self._phrase_matcher = PhraseMatcher(self._nlp.vocab, "LEMMA")
        self._use_child_cui_label = use_child_cui_label
        self._min_phrase_length = min_phrase_length

    def add_parent_cui(self, parent_cui: int, snomed_lookup: SnomedLookup):
        cui_to_synonyms = {}
        cui_to_synonyms[parent_cui] = snomed_lookup.cui_to_synonyms[parent_cui]

        for child_cui in snomed_lookup.get_child_cuis(parent_cui):
            child_synonyms = snomed_lookup.cui_to_synonyms[child_cui]
            if self._use_child_cui_label:
                cui_to_synonyms[child_cui] = child_synonyms
            else:
                cui_to_synonyms[parent_cui].union(child_synonyms)

        synonym_lengths = np.cumsum([0] + list(map(len, cui_to_synonyms.values())))
        flattened_synonyms = [
            synonym for synonyms in cui_to_synonyms.values() for synonym in synonyms
        ]
        synonym_docs = list(self._nlp.pipe(flattened_synonyms))

        for index, cui in enumerate(cui_to_synonyms.keys()):
            cui_synonym_docs = synonym_docs[
                synonym_lengths[index] : synonym_lengths[index + 1]
            ]
            self._phrase_matcher.add(str(cui), cui_synonym_docs)

    def add_non_snomed_term(self, custom_cui: int, term: str):
        self._phrase_matcher.add(str(custom_cui), [self._nlp(term)])

    def _span_is_valid_length(self, span) -> bool:
        acronym_min_length = 2
        word_min_length = 3
        span_char_length = span.end_char - span.start_char

        if span.text.isupper():
            return span_char_length >= acronym_min_length
        return span_char_length >= word_min_length

    def _annotate_doc(self, doc: Doc, resolve_overlaps: bool) -> List[Span]:
        snomed_matches = self._phrase_matcher(doc, as_spans=True)
        # Catch edge cases such as anxiety/depression
        if not snomed_matches and "/" in doc.text:
            doc_v2 = self._nlp(doc.text.replace("/", " "))
            snomed_matches = self._phrase_matcher(doc_v2, as_spans=True)
        # When spans overlap, the (first) longest span is preferred
        filtered_snomed_matches = [
            span for span in snomed_matches if self._span_is_valid_length(span)
        ]
        if resolve_overlaps:
            filtered_snomed_matches = filter_spans(filtered_snomed_matches)
        return filtered_snomed_matches

    def __call__(self, text: str, resolve_overlaps=True) -> List[Span]:
        doc = self._nlp(text)
        return self._annotate_doc(doc, resolve_overlaps)

    def pipe(self, texts: Iterable[str], resolve_overlaps=True) -> List[List[Span]]:
        docs = self._nlp.pipe([text for text in texts])
        return [self._annotate_doc(doc, resolve_overlaps) for doc in docs]
