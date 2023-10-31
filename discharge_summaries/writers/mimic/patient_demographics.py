from copy import deepcopy
from typing import Any, Dict, List


from discharge_summaries.openai_llm.chat_models import AzureOpenAIChatModel
from discharge_summaries.schemas.prsb_guidelines import PatientDemographics
from discharge_summaries.writers.mimic.utils import (
    pydantic_def_to_simplified_json_schema,
    query_llm_to_fill_json_schema,
    remove_filled_fields_from_schema,
)


class PatientDemographicsWriter:
    def __init__(self, llm: AzureOpenAIChatModel):
        self.llm = llm
        self.json_schema = pydantic_def_to_simplified_json_schema(PatientDemographics)

    def run(
        self, physician_notes: List[str], structured_data: Dict
    ) -> PatientDemographics:
        structured_data = self._complete_from_structured_data(structured_data)
        missing_fields_schema = deepcopy(self.json_schema)
        missing_fields_schema = remove_filled_fields_from_schema(
            missing_fields_schema["properties"], structured_data
        )
        physician_note_data = self._complete_from_physician_notes(
            physician_notes, missing_fields_schema
        )
        return PatientDemographics(**physician_note_data, **structured_data)

    def _complete_from_structured_data(self, structured_data: Dict) -> Dict[str, Any]:
        admission_series = structured_data["admission_series"]
        patient_series = structured_data["patient_series"]

        return {
            "other_identifier": [f"subject_id: {admission_series['SUBJECT_ID']}"],
            "date_of_birth": patient_series["DOB"].split(" ")[0],
            "gender": patient_series["GENDER"],
            "nhs_number": "MIMIC is a US dataset so NHS Number is not applicable/known",
            "patient_address": "Removed from database",
            "patient_email_address": "Removed from database for anonymity",
            "patient_telephone_number": "Removed from database for anonymity",
            "relevant_contacts": "Removed from database for anonymity",
        }

    def _complete_from_physician_notes(
        self, physician_notes: List[str], unstructured_data_json_schema: Dict
    ) -> Dict[str, Any]:
        return query_llm_to_fill_json_schema(
            physician_notes[:1], unstructured_data_json_schema, self.llm
        )
