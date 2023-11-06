from collections import defaultdict
from typing import Dict, List, Set, Tuple

from spacy.language import Language
from spacy.tokens import Span

from .lookup import SnomedLookup
from .phrase_matcher import SnomedPhraseMatcher


class SnomedRetriever:
    def __init__(
        self,
        base_snomed_phrase_matcher: SnomedPhraseMatcher,
        snomed_lookup: SnomedLookup,
        nlp_with_sentence_segmenter: Language,
    ) -> None:
        self._base_snomed_phrase_matcher = base_snomed_phrase_matcher
        self._snomed_lookup = snomed_lookup
        self._nlp_with_sentence_segmenter = nlp_with_sentence_segmenter

    def _create_custom_phrase_matcher(
        self, search_term_to_cuis: Dict[str, List[int]]
    ) -> SnomedPhraseMatcher:
        custom_phrase_matcher = SnomedPhraseMatcher(
            self._nlp_with_sentence_segmenter, False
        )
        for cui in {cui for cuis in search_term_to_cuis.values() for cui in cuis}:
            custom_phrase_matcher.add_parent_cui(int(cui), self._snomed_lookup)

        unmatched_finding_cui = -1
        for finding, cuis in search_term_to_cuis.items():
            if not cuis:
                custom_phrase_matcher.add_non_snomed_term(
                    unmatched_finding_cui, finding
                )
                search_term_to_cuis[finding] = [unmatched_finding_cui]
                unmatched_finding_cui -= 1
        return custom_phrase_matcher

    def __call__(
        self, texts: List[str], search_terms: Set[str]
    ) -> Dict[str, List[Tuple[int, Span]]]:
        search_cuis = [
            [int(ent.label_) for ent in finding_doc.ents]
            for finding_doc in self._base_snomed_phrase_matcher.pipe(search_terms)
        ]
        search_term_to_cuis = {
            term: cuis for term, cuis in zip(search_terms, search_cuis)
        }
        custom_phrase_matcher = self._create_custom_phrase_matcher(search_term_to_cuis)

        annotated_notes = custom_phrase_matcher.pipe(texts)
        cui_to_note_idx_and_sent = defaultdict(list)
        for note_idx, annotated_note in enumerate(annotated_notes):
            for ent in annotated_note.ents:
                cui_to_note_idx_and_sent[int(ent.label_)].append((note_idx, ent.sent))

        search_term_to_note_start_idxs_and_sents = {
            search_term: sorted(
                note_idx_and_sent
                for cui in cuis
                for note_idx_and_sent in cui_to_note_idx_and_sent[cui]
            )
            for search_term, cuis in search_term_to_cuis.items()
        }
        for (
            search_term,
            note_idx_and_sents,
        ) in search_term_to_note_start_idxs_and_sents.items():
            seen: Set[str] = set()
            seen_add = seen.add
            search_term_to_note_start_idxs_and_sents[search_term] = [
                (note_idx, sent)
                for note_idx, sent in note_idx_and_sents
                if not (sent.text in seen or seen_add(sent.text))
            ]

        return search_term_to_note_start_idxs_and_sents
