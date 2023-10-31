from copy import deepcopy
from typing import Any, Dict, List

import pandas as pd

from discharge_summaries.openai_llm.chat_models import AzureOpenAIChatModel
from discharge_summaries.schemas.prsb_guidelines import AdmissionDetails
from discharge_summaries.writers.mimic.utils import (
    pydantic_def_to_simplified_json_schema,
    query_llm_to_fill_json_schema,
    remove_filled_fields_from_schema,
)


class AdmissionDetailsWriter:
    def __init__(self, admissions_df: pd.DataFrame, llm: AzureOpenAIChatModel):
        self.admissions_df = admissions_df
        self.llm = llm
        self.json_schema = pydantic_def_to_simplified_json_schema(AdmissionDetails)

    def run(self, physician_notes: List[str], hadm_id: str) -> AdmissionDetails:
        structured_data = self._extract_structured_data(hadm_id)
        missing_fields_schema = deepcopy(self.json_schema)
        missing_fields_schema = remove_filled_fields_from_schema(
            missing_fields_schema["properties"], structured_data
        )
        unstructured_data = self._extract_unstructured_data(
            physician_notes, missing_fields_schema
        )
        print(unstructured_data)
        return AdmissionDetails(**unstructured_data, **structured_data)

    def _extract_structured_data(self, hadm_id) -> Dict[str, Any]:
        hadim_admission_series = self.admissions_df[
            self.admissions_df["HADM_ID"] == hadm_id
        ].iloc[0]
        return {
            "admission_method": hadim_admission_series["ADMISSION_TYPE"],
            "source_of_admission": hadim_admission_series["ADMISSION_LOCATION"],
            "date_time_of_admission": hadim_admission_series["ADMITTIME"].strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

    def _extract_unstructured_data(
        self, physician_notes: List[str], unstructured_data_json_schema: Dict
    ) -> Dict[str, Any]:
        return query_llm_to_fill_json_schema(
            physician_notes[:1], unstructured_data_json_schema, self.llm
        )
