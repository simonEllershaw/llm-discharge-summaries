from typing import Any, Dict, List

from discharge_summaries.openai_llm.chat_models import AzureOpenAIChatModel
from discharge_summaries.schemas.prsb_guidelines import ReferrerDetails
from discharge_summaries.writers.mimic.utils import (
    pydantic_def_to_simplified_json_schema,
    query_llm_to_fill_json_schema,
)


class ReferrerDetailsWriter:
    def __init__(self, llm: AzureOpenAIChatModel):
        self.llm = llm
        self.json_schema = pydantic_def_to_simplified_json_schema(ReferrerDetails)

    def run(self, physician_notes: List[str], hadm_id: str) -> ReferrerDetails:
        unstructured_data = self._extract_unstructured_data(
            physician_notes, self.json_schema
        )
        return ReferrerDetails(
            **unstructured_data,
        )

    def _extract_unstructured_data(
        self, physician_notes: List[str], unstructured_data_json_schema: Dict
    ) -> Dict[str, Any]:
        return query_llm_to_fill_json_schema(
            physician_notes[:1], unstructured_data_json_schema, self.llm
        )
