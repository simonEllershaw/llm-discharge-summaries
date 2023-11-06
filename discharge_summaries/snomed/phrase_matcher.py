from typing import Iterable, List

from spacy.language import Language
from spacy.matcher import PhraseMatcher
from spacy.tokens import Doc
from spacy.util import filter_spans

from .lookup import SnomedLookup


@Language.component("lower_case_lemmas")
def lower_case_lemmas(doc: Doc) -> Doc:
    for token in doc:
        token.lemma_ = token.lemma_.lower()
    return doc


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
            child_synonyms = snomed_lookup.cui_to_synonyms[child_cui]
            if self._use_child_cui_label:
                cui_to_synonyms[child_cui] = child_synonyms
            else:
                cui_to_synonyms[parent_cui].union(child_synonyms)

        for cui, synonyms in cui_to_synonyms.items():
            self._phrase_matcher.add(str(cui), list(self._nlp.pipe(synonyms)))

    def add_non_snomed_term(self, custom_cui: int, term: str):
        self._phrase_matcher.add(str(custom_cui), [self._nlp(term)])

    def _annotate_doc(self, doc: Doc) -> Doc:
        snomed_matches = self._phrase_matcher(doc, as_spans=True)
        # When spans overlap, the (first) longest span is preferred
        filtered_snomed_matches = filter_spans(snomed_matches)
        # Catch edge cases such as anxiety/depression
        if not filtered_snomed_matches and "/" in doc.text:
            return self(doc.text.replace("/", " "))
        doc.set_ents(filtered_snomed_matches)
        return doc

    def __call__(self, text: str) -> Doc:
        doc = self._nlp(text)
        self._annotate_doc(doc)
        return doc

    def pipe(self, texts: Iterable[str]) -> List[Doc]:
        docs = self._nlp.pipe([text for text in texts])
        return [self._annotate_doc(doc) for doc in docs]
