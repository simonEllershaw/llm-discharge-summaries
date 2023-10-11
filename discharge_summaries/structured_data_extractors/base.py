from pathlib import Path
from typing import List

from discharge_summaries.schemas.prsb_guidelines import (
    AdmissionDetails,
    AllergyOrAdverseReaction,
    Diagnosis,
    DischargeSummary,
    ExpectationsAndWishes,
    InvestigationResult,
    LegalInformation,
    MedicationAndMedicalDevices,
    PatientDemographics,
    PlanAndRequestedActions,
    Procedure,
    ReferrerDetails,
    SafetyAlerts,
    SocialContext,
)


class BaseStructuredDataExtractor:
    """Fills all PRSB Discharge Summary fields with empty strings or empty lists."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def complete_patient_demographics(self, hadm_id: str) -> PatientDemographics:
        return PatientDemographics(
            patient_name="",
            patient_preferred_name="",
            date_of_birth="",
            gender="",
            # MIMIC is a US dataset so NHS Number is not applicable/known
            nhs_number="",
            other_identifier=[],
            patient_address="",
            patient_email_address="",
            patient_telephone_number="",
            relevant_contacts="",
        )

    def complete_referrer_details(self, hadm_id) -> ReferrerDetails:
        return ReferrerDetails(
            name="", role="", grade="", organisation="", contact_details=""
        )

    def complete_social_context(self, hadm_id) -> SocialContext:
        return SocialContext(
            household_composition="", occupational_history=[], educational_history=""
        )

    def complete_individual_requirements(self, hadm_id) -> List[str]:
        return []

    def complete_participation_in_research(self, hadm_id) -> List[str]:
        return []

    def complete_admission_details(self, hadm_id: str) -> AdmissionDetails:
        return AdmissionDetails(
            reason_for_admission="",
            admission_method="",
            source_of_admission="",
            date_time_of_admission="",
        )

    def complete_diagnoses(self, hadm_id: str) -> List[Diagnosis]:
        return []

    def complete_procedures(self, hadm_id: str) -> List[Procedure]:
        return []

    def complete_clinical_summary(self, hadm_id: str) -> str:
        return ""

    def complete_investigation_results(self, hadm_id: str) -> List[InvestigationResult]:
        return []

    def complete_assessment_scale(self, hadm_id: str) -> List[str]:
        return []

    def complete_legal_information(self, hadm_id: str) -> LegalInformation:
        return LegalInformation(
            consent_for_treatment_record="",
            consent_for_information_sharing="",
            consent_relation_to_child="",
            mental_capacity_assessment="",
            advance_decision_to_refuse_treatment="",
            lasting_power_of_attorney_for_personal_wealfare_or_court_appointed_deputy=(
                ""
            ),
            organ_and_tissue_donation="",
            safeguarding_issues="",
        )

    def complete_safety_alerts(self, hadm_id: str) -> SafetyAlerts:
        return SafetyAlerts(
            risk_to_self="",
            risk_to_others="",
            risk_from_others="",
        )

    def complete_medications_and_medical_devices(
        self, hadm_id: str
    ) -> MedicationAndMedicalDevices:
        return MedicationAndMedicalDevices(
            medication_item_cluster=[],
            medication_change_summary_cluster=[],
            medical_device_entry=[],
            medication_discontinued_item_cluster=[],
        )

    def complete_allergies_and_adverse_reactions(
        self, hadm_id: str
    ) -> List[AllergyOrAdverseReaction]:
        return []

    def complete_expectations_and_wishes(self, hadm_id: str) -> ExpectationsAndWishes:
        return ExpectationsAndWishes(
            expectations_and_wishes="",
            advance_statement="",
        )

    def complete_information_and_advice_given(self, hadm_id: str) -> str:
        return ""

    def complete_plan_and_requested_actions(
        self, hadm_id: str
    ) -> PlanAndRequestedActions:
        return PlanAndRequestedActions(
            actions_for_healthcare_professionals=[],
            actions_for_patient_or_their_carer=[],
            agreed_with_patient_or_legitimate_patient_representative="",
            investigations_requested=[],
            procedures_requested=[],
        )

    def complete_prsb_discharge_summary(self, hadm_id: str) -> DischargeSummary:
        return DischargeSummary(
            patient_demographics=self.complete_patient_demographics(hadm_id),
            referrer_details=self.complete_referrer_details(hadm_id),
            social_context=self.complete_social_context(hadm_id),
            individual_requirements=self.complete_individual_requirements(hadm_id),
            participation_in_research=self.complete_participation_in_research(hadm_id),
            admission_details=self.complete_admission_details(hadm_id),
            diagnoses=self.complete_diagnoses(hadm_id),
            procedures=self.complete_procedures(hadm_id),
            clinical_summary=self.complete_clinical_summary(hadm_id),
            investigation_results=self.complete_investigation_results(hadm_id),
            assessment_scale=self.complete_assessment_scale(hadm_id),
            legal_information=self.complete_legal_information(hadm_id),
            safety_alerts=self.complete_safety_alerts(hadm_id),
            medications_and_medical_devices=self.complete_medications_and_medical_devices(
                hadm_id
            ),
            allergies_and_adverse_reactions=self.complete_allergies_and_adverse_reactions(
                hadm_id
            ),
            expectations_and_wishes=self.complete_expectations_and_wishes(hadm_id),
            information_and_advice_given=self.complete_information_and_advice_given(
                hadm_id
            ),
            plan_and_requested_actions=self.complete_plan_and_requested_actions(
                hadm_id
            ),
        )
