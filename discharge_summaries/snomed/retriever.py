from collections import defaultdict
from typing import Dict, List, Set

from spacy.tokens import Span

from .lookup import SnomedLookup
from .phrase_matcher import SnomedPhraseMatcher


class SnomedRetriever:
    def __init__(
        self,
        snomed_phrase_matcher: SnomedPhraseMatcher,
        snomed_lookup: SnomedLookup,
        token_window_size: int = 50,
    ) -> None:
        self._snomed_phrase_matcher = snomed_phrase_matcher
        self._snomed_lookup = snomed_lookup
        self._token_window_size = token_window_size

    def _get_cui_to_search_terms(self, search_terms: Set[str], include_child_cuis=True):
        search_cuis = [
            [int(ent.label_) for ent in finding_doc.ents]
            for finding_doc in self._snomed_phrase_matcher.pipe(search_terms)
        ]
        search_term_to_cuis = {
            term: cuis for term, cuis in zip(search_terms, search_cuis)
        }
        cui_to_search_term = defaultdict(set)
        for search_term, cuis in search_term_to_cuis.items():
            for cui in cuis:
                cui_to_search_term[cui].add(search_term)
                if include_child_cuis:
                    for child_cui in self._snomed_lookup.get_child_cuis(cui):
                        cui_to_search_term[child_cui].add(search_term)
        return cui_to_search_term

    @staticmethod
    def _merge_overlapping_sorted_spans(spans: List[Span]) -> List[Span]:
        if len(spans) <= 1:
            return spans
        merged_spans = []
        current_span = spans[0]
        for span in spans[1:]:
            if span.doc == current_span.doc and span.start <= current_span.end:
                if span.end >= current_span.end:
                    current_span.end = span.end
                else:
                    # Span is dropped if sub span
                    pass
            else:
                merged_spans.append(current_span)
                current_span = span
        merged_spans.append(current_span)
        return merged_spans

    @staticmethod
    def _filter_repeated_span_texts(spans: List[Span]) -> List[Span]:
        seen_span_texts: Set[str] = set()
        seen_add = seen_span_texts.add
        return [
            span
            for span in spans
            if not (span.text in seen_span_texts or seen_add(span.text))
        ]

    def __call__(
        self, texts: List[str], search_terms: Set[str]
    ) -> Dict[str, List[Span]]:
        cui_to_search_terms = self._get_cui_to_search_terms(search_terms)
        search_term_to_extract_spans = defaultdict(list)
        for idx, doc in enumerate(self._snomed_phrase_matcher.pipe(texts)):
            doc.user_data = {"idx": idx}
            for ent in doc.ents:
                for ent_search_term in cui_to_search_terms.get(int(ent.label_), set()):
                    search_term_to_extract_spans[ent_search_term].append(
                        Span(
                            doc,
                            max(0, ent.start - self._token_window_size),
                            min(ent.end + self._token_window_size, len(ent.doc)),
                        )
                    )

        search_term_to_filtered_extract_spans = {
            search_term: self._filter_repeated_span_texts(
                self._merge_overlapping_sorted_spans(extract_spans)
            )
            for search_term, extract_spans in search_term_to_extract_spans.items()
        }

        return search_term_to_filtered_extract_spans
