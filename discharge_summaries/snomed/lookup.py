import json
import re
from pathlib import Path
from typing import Dict, Optional, Set, Tuple

import pandas as pd


class SnomedLookup:
    PREFERRED_TERM_ID = "900000000000003001"
    SYNONYM_TERM_ID = "900000000000013009"
    IS_A_RELATIONSHIP_ID = "116680003"

    ACRONYM_REGEX = re.compile(r"^[A-Z]{2,4}(?= - )")

    def __init__(
        self,
        cui_to_preferred_term: Dict[int, str],
        cui_to_synonyms: Dict[int, Set[str]],
        parent_cui_to_child_cuis: Dict[int, Set[int]],
    ) -> None:
        self.cui_to_preferred_term = cui_to_preferred_term
        self.cui_to_synonyms = cui_to_synonyms
        self.parent_cui_to_child_cuis = parent_cui_to_child_cuis

    # def get_cuis(self, name: str) -> Set[int]:
    #     return {
    #         cui
    #         for cui, synonyms in self.cui_to_synonyms.items()
    #         if name.lower() in synonyms
    #     }

    def get_child_cuis(self, parent_cui: int) -> Set[int]:
        direct_child_cuis = self.parent_cui_to_child_cuis.get(parent_cui, set())
        if not direct_child_cuis:
            return set()
        else:
            recursive_child_cuis = {
                recursive_child_cui
                for child_cui in direct_child_cuis
                for recursive_child_cui in self.get_child_cuis(child_cui)
            }
            return direct_child_cuis.union(recursive_child_cuis)

    @staticmethod
    def _parse_snomed_file(
        filename: Path, first_row_header=True, columns=None
    ) -> pd.DataFrame:
        with open(filename, encoding="utf-8") as f:
            entities = [[n.strip() for n in line.split("\t")] for line in f]
            return pd.DataFrame(
                entities[1:], columns=entities[0] if first_row_header else columns
            )

    @staticmethod
    def _load_active_cuis_from_file(
        int_concept_filepath: Path,
        uk_ext_concept_filepath: Path,
        drug_ext_concept_filepath: Path,
    ) -> Set[int]:
        int_concept_df = SnomedLookup._parse_snomed_file(int_concept_filepath)
        uk_concept_df = SnomedLookup._parse_snomed_file(uk_ext_concept_filepath)
        drug_concept_df = SnomedLookup._parse_snomed_file(drug_ext_concept_filepath)

        concept_df = pd.concat(
            [int_concept_df, uk_concept_df, drug_concept_df], ignore_index=True
        )
        concept_df = concept_df[concept_df.active == "1"]
        return set(concept_df.id.astype("int64").tolist())

    @staticmethod
    def _extract_acronym(row: pd.Series) -> Optional[pd.Series]:
        match = SnomedLookup.ACRONYM_REGEX.match(row["name"])
        if match and match.group(0) != len(row["name"]):
            return {"cui": row["cui"], "name": match.group(0)}
        else:
            return None

    @staticmethod
    def _load_preferred_and_synonym_dfs_from_file(
        int_description_filepath: Path,
        uk_ext_description_filepath: Path,
        drug_ext_description_filepath: Path,
        active_cuis: Set[int],
    ) -> Tuple[Dict[int, str], Dict[int, Set[str]]]:
        int_description_df = SnomedLookup._parse_snomed_file(int_description_filepath)
        uk_description_df = SnomedLookup._parse_snomed_file(uk_ext_description_filepath)
        drug_description_df = SnomedLookup._parse_snomed_file(
            drug_ext_description_filepath
        )
        description_df = pd.concat(
            [int_description_df, uk_description_df, drug_description_df],
            ignore_index=True,
        )
        description_df = description_df[description_df.active == "1"]

        description_df.rename(
            columns={"term": "name", "conceptId": "cui"}, inplace=True
        )
        description_df = description_df[["cui", "name", "typeId"]].copy()
        description_df["cui"] = description_df["cui"].astype("int64")
        description_df["name"] = description_df["name"].astype("string")
        description_df = description_df[description_df["cui"].isin(active_cuis)]

        preferred_terms_df = description_df[
            description_df["typeId"] == SnomedLookup.PREFERRED_TERM_ID
        ].copy()
        preferred_terms_df.drop(columns=["typeId"], inplace=True)
        preferred_terms_df["name"] = preferred_terms_df.apply(
            lambda row: re.sub(r" \(.*?\)$", "", row["name"]), axis=1
        )
        preferred_terms_df = preferred_terms_df.drop_duplicates(["cui"], keep="first")
        preferred_terms_df = preferred_terms_df.set_index("cui")
        cui_to_preferred_term = preferred_terms_df.to_dict()["name"]

        synonyms_df = description_df[
            description_df["typeId"] == SnomedLookup.SYNONYM_TERM_ID
        ].copy()
        synonyms_df.drop(columns=["typeId"], inplace=True)
        acronyms_df = pd.DataFrame(
            synonyms_df.apply(SnomedLookup._extract_acronym, axis=1)
            .dropna()
            .reset_index(drop=True)
            .tolist()
        )
        acronyms_df.drop_duplicates(inplace=True)
        synonyms_df = pd.concat([synonyms_df, acronyms_df])
        synonyms_df = synonyms_df.drop_duplicates()
        synonyms_df = (
            synonyms_df.groupby("cui")["name"].apply(set).reset_index().set_index("cui")
        )
        cui_to_synonyms = synonyms_df.to_dict()["name"]

        return cui_to_preferred_term, cui_to_synonyms

    @staticmethod
    def _relation_file_parent_to_child_cui_dict(
        int_relations_filepath: Path,
        uk_ext_relations_filepath: Path,
        drug_ext_relations_filepath: Path,
        active_cuis: Set[int],
    ) -> Dict[int, Set[int]]:
        int_relations_df = SnomedLookup._parse_snomed_file(int_relations_filepath)
        uk_relations_df = SnomedLookup._parse_snomed_file(uk_ext_relations_filepath)
        drug_relations_df = SnomedLookup._parse_snomed_file(drug_ext_relations_filepath)

        relations_df = pd.concat(
            [int_relations_df, uk_relations_df, drug_relations_df], ignore_index=True
        )
        relations_df = relations_df[relations_df.active == "1"].copy()
        relations_df = relations_df[
            relations_df.typeId == SnomedLookup.IS_A_RELATIONSHIP_ID
        ].copy()
        relations_df = relations_df.drop_duplicates()
        relations_df.rename(
            columns={"sourceId": "child_cui", "destinationId": "parent_cui"},
            inplace=True,
        )
        relations_df["child_cui"] = relations_df["child_cui"].astype("int64")
        relations_df["parent_cui"] = relations_df["parent_cui"].astype("int64")
        relations_df = relations_df[relations_df["child_cui"].isin(active_cuis)]
        relations_df = relations_df[relations_df["parent_cui"].isin(active_cuis)]
        relations_df = (
            relations_df.groupby("parent_cui")["child_cui"]
            .apply(set)
            .reset_index()
            .set_index("parent_cui")
        )

        return relations_df.to_dict()["child_cui"]

    @staticmethod
    def load_from_raw_snomed_files(
        int_concepts_fpath: Path,
        uk_ext_concepts_fpath: Path,
        uk_drug_ext_concepts_fpath: Path,
        int_descriptions_fpath: Path,
        uk_ext_descriptions_fpath: Path,
        uk_drug_ext_descriptions_fpath: Path,
        int_relations_fpath: Path,
        uk_ext_relations_fpath: Path,
        uk_drug_ext_relations_fpath: Path,
    ) -> "SnomedLookup":
        active_cuis = SnomedLookup._load_active_cuis_from_file(
            int_concepts_fpath, uk_ext_concepts_fpath, uk_drug_ext_concepts_fpath
        )

        preferred_terms_df, synonyms_df = (
            SnomedLookup._load_preferred_and_synonym_dfs_from_file(
                int_descriptions_fpath,
                uk_ext_descriptions_fpath,
                uk_drug_ext_descriptions_fpath,
                active_cuis,
            )
        )

        parent_to_child_df = SnomedLookup._relation_file_parent_to_child_cui_dict(
            int_relations_fpath,
            uk_ext_relations_fpath,
            uk_drug_ext_relations_fpath,
            active_cuis,
        )
        return SnomedLookup(preferred_terms_df, synonyms_df, parent_to_child_df)

    def save(self, dir_name: Path):
        dir_name.mkdir(parents=True, exist_ok=True)
        (dir_name / "cui_to_preferred_term.json").write_text(
            json.dumps(self.cui_to_preferred_term)
        )
        (dir_name / "cui_to_synonyms.json").write_text(
            json.dumps(
                {cui: list(synonyms) for cui, synonyms in self.cui_to_synonyms.items()}
            )
        )
        (dir_name / "parent_to_child_cuis.json").write_text(
            json.dumps(
                {
                    cui: list(synonyms)
                    for cui, synonyms in self.parent_cui_to_child_cuis.items()
                }
            )
        )

    @staticmethod
    def load(dir_name: Path):
        cui_to_preferred_term_json = json.loads(
            (dir_name / "cui_to_preferred_term.json").read_text()
        )
        cui_to_preferred_term = {
            int(cui): preferred_term
            for cui, preferred_term in cui_to_preferred_term_json.items()
        }

        cui_to_synonyms_json = json.loads(
            (dir_name / "cui_to_synonyms.json").read_text()
        )
        cui_to_synonyms = {
            int(cui): set(synonyms) for cui, synonyms in cui_to_synonyms_json.items()
        }

        parent_cui_to_child_json = json.loads(
            (dir_name / "parent_to_child_cuis.json").read_text()
        )
        parent_cui_to_child_cuis = {
            int(parent_cui): {int(cui) for cui in child_cuis}
            for parent_cui, child_cuis in parent_cui_to_child_json.items()
        }

        return SnomedLookup(
            cui_to_preferred_term, cui_to_synonyms, parent_cui_to_child_cuis
        )