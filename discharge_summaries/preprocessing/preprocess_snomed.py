import re
from collections import defaultdict
from pathlib import Path
from typing import Set, Tuple

import pandas as pd
from tqdm.notebook import tqdm


class Snomed:
    PREFERRED_TERM_ID = "900000000000003001"
    SYNONYM_TERM_ID = "900000000000013009"

    def __init__(self, description_file: Path, relation_file: Path) -> None:
        self.description_file = description_file
        self.relation_file = relation_file

        self.preferred_term_df, self.synonyms_df = self._load_name_cui_dfs()
        self.parent_to_child_cuis = self._load_parent_to_child_cuis()

    @staticmethod
    def _parse_snomed_file(
        filename: Path, first_row_header=True, columns=None
    ) -> pd.DataFrame:
        with open(filename, encoding="utf-8") as f:
            entities = [[n.strip() for n in line.split("\t")] for line in f]
            return pd.DataFrame(
                entities[1:], columns=entities[0] if first_row_header else columns
            )

    def _load_name_cui_dfs(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        description_df = self._parse_snomed_file(self.description_file)
        description_df = description_df[description_df.active == "1"]
        description_df.rename(
            columns={"term": "name", "conceptId": "cui"}, inplace=True
        )
        description_df = description_df[["cui", "name", "typeId"]].copy()

        preferred_term_df = description_df[
            description_df["typeId"] == self.PREFERRED_TERM_ID
        ].copy()
        preferred_term_df.drop(columns=["typeId"], inplace=True)
        preferred_term_df["name"] = preferred_term_df.apply(
            lambda row: re.sub(r" \(.*?\)$", "", row["name"]), axis=1
        )
        preferred_term_df = preferred_term_df.drop_duplicates(["cui"], keep="first")

        synonyms_df = description_df[
            description_df["typeId"] == self.SYNONYM_TERM_ID
        ].copy()
        synonyms_df.drop(columns=["typeId"], inplace=True)
        synonyms_df = synonyms_df.drop_duplicates()

        return preferred_term_df, synonyms_df

    def _load_parent_to_child_cuis(self):
        relation_df = self._parse_snomed_file(self.relation_file)
        relation_df = relation_df[relation_df.active == "1"].copy()
        relation_df = relation_df[relation_df.typeId == "116680003"].copy()
        relation_df = relation_df.drop_duplicates()
        relation_df.rename(
            columns={"sourceId": "source_cui", "destinationId": "destination_cui"},
            inplace=True,
        )

        parent_cui_to_child_cuis = defaultdict(set)
        for _, row in tqdm(relation_df.iterrows(), total=len(relation_df)):
            parent_cui_to_child_cuis[row.destination_cui].add(row.source_cui)

        return parent_cui_to_child_cuis

    def get_preferred_term(self, cui: str) -> str:
        return self.preferred_term_df[self.preferred_term_df.cui == cui].name.values[0]

    def get_synonyms(self, cui: str) -> str:
        return self.synonyms_df[self.synonyms_df.cui == cui].name.values.to_list()

    def get_child_cuis(self, parent_cui: str) -> Set[str]:
        direct_child_cuis = self.parent_to_child_cuis[parent_cui]
        if not direct_child_cuis:
            return set()
        else:
            recursive_child_cuis = {
                recursive_child_cui
                for child_cui in direct_child_cuis
                for recursive_child_cui in self.get_child_cuis(child_cui)
            }
            return direct_child_cuis.union(recursive_child_cuis)
