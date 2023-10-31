import re
from pathlib import Path
from typing import Dict

import pandas as pd

from discharge_summaries.openai_llm.chat_models import AzureOpenAIChatModel


class MIMICPRSBDischargeSummaryWriter:
    def __init__(self, data_dir: Path, llm: AzureOpenAIChatModel) -> None:
        self.patient_df = pd.read_csv(
            self.data_dir / "PATIENTS.csv", usecols=["SUBJECT_ID", "DOB", "GENDER"]
        )
        self.admissions_df = pd.read_csv(
            self.data_dir / "ADMISSIONS.csv",
            usecols=[
                "HADM_ID",
                "ADMITTIME",
                "DISCHTIME",
                "SUBJECT_ID",
                "ADMISSION_TYPE",
                "ADMISSION_LOCATION",
            ],
        )
        self.procedures_df = pd.read_csv(
            self.data_dir / "PROCEDUREEVENTS_MV.csv",
            usecols=["HADM_ID", "ITEMID", "LOCATION"],
        )
        self.items_df = pd.read_csv(
            self.data_dir / "D_ITEMS.csv", usecols=["ITEMID", "LABEL"]
        )
        self.prescriptions_df = pd.read_csv(
            self.data_dir / "PRESCRIPTIONS.csv",
            usecols=[
                "HADM_ID",
                "DRUG",
                "STARTDATE",
                "ENDDATE",
                "DOSE_VAL_RX",
                "DOSE_UNIT_RX",
                "ROUTE",
                "FORM_VAL_DISP",
                "FORM_UNIT_DISP",
            ],
        )

        self.admissions_df["ADMITTIME"] = pd.to_datetime(
            self.admissions_df["ADMITTIME"], format="%Y-%m-%d %H:%M:%S"
        )
        self.admissions_df["DISCHTIME"] = pd.to_datetime(
            self.admissions_df["DISCHTIME"], format="%Y-%m-%d %H:%M:%S"
        )
        self.procedures_df = pd.merge(
            self.procedures_df,
            self.items_df[["ITEMID", "LABEL"]],
            on="ITEMID",
            how="inner",
        )
        self.procedures_df["LOCATION"] = self.procedures_df["LOCATION"].astype(str)
        self.procedures_df["ANATOMICAL_SITE"] = self.procedures_df["LOCATION"].apply(
            self._location_to_anatomical_site
        )
        self.procedures_df["LATERALITY"] = self.procedures_df["LOCATION"].apply(
            self._location_to_laterality
        )
        self.procedures_df = self.procedures_df[
            ["HADM_ID", "LABEL", "ANATOMICAL_SITE", "LATERALITY"]
        ]
        self.procedures_df = self.procedures_df.drop_duplicates()

        # Remove times from dates as all set to 00:00:00
        self.prescriptions_df["STARTDATE"] = self.prescriptions_df["STARTDATE"].apply(
            lambda x: str(x).split(" ")[0]
        )
        self.prescriptions_df["ENDDATE"] = self.prescriptions_df["ENDDATE"].apply(
            lambda x: str(x).split(" ")[0]
        )
        self.llm = llm

    @staticmethod
    def _location_to_anatomical_site(location: str) -> str:
        if location == "nan":
            return ""
        return re.sub("(?i)^(RIGHT|LEFT|RU|RL|LU|LL|R|L) ", "", location)

    @staticmethod
    def _location_to_laterality(location: str) -> str:
        if re.match("(?i)^(RIGHT|RU|RL|R) ", location):
            return "Right"
        elif re.match("(?i)^(LEFT|LU|LL|L) ", location):
            return "Left"
        else:
            return ""

    def _extract_hadm_id_structure_date(self, hadm_id: str) -> Dict:
        admissions_series = self.admissions_df[
            self.admissions_df["HADM_ID"] == hadm_id
        ].iloc[0]
        subject_id = admissions_series["SUBJECT_ID"]
        patient_series = self.patient_df[
            self.patient_df["SUBJECT_ID"] == subject_id
        ].iloc[0]

        return {
            "admissions_series": admissions_series,
            "patient_series": patient_series,
        }

    def run(self, hadm_id: str) -> str:
        self._extract_hadm_id_structure_date(hadm_id)

    # def complete_patient_demographics(self, hadm_id: str) -> PatientDemographics:
    #     hadm_id_admissions_series = self.admissions_df[
    #         self.admissions_df["HADM_ID"] == hadm_id
    #     ].iloc[0]
    #     subject_id = hadm_id_admissions_series["SUBJECT_ID"]
    #     hadm_id_patient_series = self.patient_df[
    #         self.patient_df["SUBJECT_ID"] == subject_id
    #     ].iloc[0]

    #     return PatientDemographics(
    #         patient_name="",
    #         patient_preferred_name="",
    #         date_of_birth=hadm_id_patient_series["DOB"].split(" ")[0],
    #         gender=hadm_id_patient_series["GENDER"],
    #         # MIMIC is a US dataset so NHS Number is not applicable/known
    #         nhs_number="Not known",
    #         other_identifier=[f"subject_id: {subject_id}"],
    #         patient_address="Removed from database",
    #         patient_email_address="Removed from database for anonymity",
    #         patient_telephone_number="Removed from database for anonymity",
    #         relevant_contacts="Removed from database for anonymity",
    #     )

    # def complete_admission_details(self, hadm_id: str) -> AdmissionDetails:
    #     hadim_admission_series = self.admissions_df[
    #         self.admissions_df["HADM_ID"] == hadm_id
    #     ].iloc[0]
    #     return AdmissionDetails(
    #         reason_for_admission="",
    #         admission_method=hadim_admission_series["ADMISSION_TYPE"],
    #         source_of_admission=hadim_admission_series["ADMISSION_LOCATION"],
    #         date_time_of_admission=hadim_admission_series["ADMITTIME"].strftime(
    #             "%Y-%m-%d %H:%M:%S"
    #         ),
    #     )

    # def complete_procedures(self, hadm_id: str) -> List[Procedure]:
    #     hadim_procedures_df = self.procedures_df[
    #         self.procedures_df["HADM_ID"] == hadm_id
    #     ]
    #     return [
    #         Procedure(
    #             procedure_name=procedure_name,
    #             anatomical_site=procedure_df["ANATOMICAL_SITE"].values[0],
    #             laterality=procedure_df["LATERALITY"].values[0],
    #             complications_related_to_procedure=[],
    #             specific_anaesthesia_issues=[],
    #             comment="",
    #         )
    #         for procedure_name, procedure_df in hadim_procedures_df.groupby("LABEL")
    #     ]

    # def complete_legal_information(self, hadm_id: str) -> LegalInformation:
    #     return LegalInformation(
    #         consent_for_treatment_record="",
    #         consent_for_information_sharing="",
    #         consent_relation_to_child="",
    #         mental_capacity_assessment="",
    #         advance_decision_to_refuse_treatment="",
    #         lasting_power_of_attorney_for_personal_wealfare_or_court_appointed_deputy=(
    #             ""
    #         ),
    #         organ_and_tissue_donation="",
    #         safeguarding_issues="",
    #     )

    # def _fill_discontinued_medication_item(
    #     self, most_recent_prescription: pd.Series
    # ) -> MedicationDiscontinued:
    #     return MedicationDiscontinued(
    #         name_of_discontinued_medication=most_recent_prescription["DRUG"],
    #         status="Discontinued",
    #         indication="",
    #         date_of_latest_change=most_recent_prescription["ENDDATE"],
    #         description_of_amendment="",
    #         comment="",
    #     )

    # def _fill_medication_item(
    #     self, most_recent_prescription: pd.Series
    # ) -> MedicationItem:
    #     return MedicationItem(
    #         medication_name=most_recent_prescription["DRUG"],
    #         form=most_recent_prescription["FORM_UNIT_DISP"],
    #         quantity_supplied=[
    #             f'{most_recent_prescription["FORM_VAL_DISP"]} {most_recent_prescription["FORM_UNIT_DISP"]}'
    #         ],
    #         route=[most_recent_prescription["ROUTE"]],
    #         site="",
    #         method="",
    #         dose_amount_description=(
    #             f'{most_recent_prescription["DOSE_VAL_RX"]} {most_recent_prescription["DOSE_UNIT_RX"]}'
    #         ),
    #         dose_timing_description="",
    #         dose_direction_duration="",
    #         additional_instruction="",
    #     )

    # def _fill_medication_change_item(
    #     self,
    #     item_entry: MedicationItem,
    #     most_recent_prescription: pd.Series,
    #     status: str,
    # ) -> MedicationChangeItem:
    #     medication_change_summary = MedicationChangeSummary(
    #         status=status,
    #         indication="",
    #         date_of_latest_change=most_recent_prescription["STARTDATE"],
    #         description_of_amendment="",
    #     )
    #     return MedicationChangeItem(
    #         medication_change_summary=medication_change_summary, **item_entry.dict()
    #     )

    # def complete_medications_and_medical_devices(
    #     self, hadm_id: str
    # ) -> MedicationAndMedicalDevices:
    #     hadm_id_admissions_series = self.admissions_df[
    #         self.admissions_df["HADM_ID"] == hadm_id
    #     ].iloc[0]
    #     admission_date = hadm_id_admissions_series["ADMITTIME"].strftime("%Y-%m-%d")
    #     discharge_date = hadm_id_admissions_series["DISCHTIME"].strftime("%Y-%m-%d")

    #     hadm_id_prescriptions_df = self.prescriptions_df[
    #         self.prescriptions_df["HADM_ID"] == hadm_id
    #     ]

    #     medication_item_cluster = []
    #     medication_change_summary_cluster = []
    #     medication_discontinued_item_cluster = []
    #     for _, drug_df in hadm_id_prescriptions_df.groupby("DRUG"):
    #         initial_prescription = drug_df.sort_values(
    #             "STARTDATE", ascending=True
    #         ).iloc[0]
    #         most_recent_prescription = drug_df.sort_values(
    #             "ENDDATE", ascending=False
    #         ).iloc[0]

    #         # Discharge summary should NOT include details of medications
    #         # that were both started and stopped in hospitals
    #         if (
    #             initial_prescription["STARTDATE"] > admission_date
    #             and most_recent_prescription["ENDDATE"] < discharge_date
    #         ):
    #             continue
    #         # Medications that were current at the time of admission which
    #         # were discontinued either during the admission or at the time of discharge
    #         elif most_recent_prescription["ENDDATE"] < discharge_date:
    #             medication_discontinued_item_cluster.append(
    #                 self._fill_discontinued_medication_item(most_recent_prescription)
    #             )
    #         else:
    #             medication_item = self._fill_medication_item(most_recent_prescription)

    #             # Medicine present on discharge but not on admission
    #             if initial_prescription["STARTDATE"] != admission_date:
    #                 medication_change_summary_cluster.append(
    #                     self._fill_medication_change_item(
    #                         medication_item, most_recent_prescription, "Added"
    #                     )
    #                 )
    #             # Medicine present on both admission and discharge but with amendment(s) since admission
    #             elif len(drug_df) > 1:
    #                 medication_change_summary_cluster.append(
    #                     self._fill_medication_change_item(
    #                         medication_item, most_recent_prescription, "Amended"
    #                     )
    #                 )
    #             # Medication is unchanged from admission to discharge
    #             else:
    #                 medication_item_cluster.append(medication_item)
    #     return MedicationAndMedicalDevices(
    #         medication_item_cluster=medication_item_cluster,
    #         medication_change_summary_cluster=medication_change_summary_cluster,
    #         medical_device_entry=[],
    #         medication_discontinued_item_cluster=medication_discontinued_item_cluster,
    #     )

    # def run():
    #     hadm_id_admissions_series = self.admissions_df[
    #         self.admissions_df["HADM_ID"] == hadm_id
    #     ].iloc[0]
    #     subject_id = hadm_id_admissions_series["SUBJECT_ID"]
    #     hadm_id_patient_series = self.patient_df[
    #         self.patient_df["SUBJECT_ID"] == subject_id
    #     ].iloc[0]
