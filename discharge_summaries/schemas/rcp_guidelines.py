from typing import List

from pydantic import BaseModel, Field


class PatientDemographics(BaseModel):
    safety_alerts: List[str] = Field(
        description=(
            "Any alerts could be documented here eg treatment limitation decisions,"
            " multi-resistant organisms, refusal of specific managements eg blood"
            " products; safeguarding concerns. This includes risks to self (eg suicide,"
            " overdose, self-harm, neglect), to others (to carers, professionals or"
            " others) and risks from others (risk from an identified person eg family"
            " member)."
        )
    )


class SocialContext(BaseModel):
    social_context: str = Field(
        description=(
            "Includes elements such as lifestyle factors eg smoking status, alcohol,"
            " and social context, eg whether the person lives alone. This is"
            " particularly important if the admission and discharge locations differ."
            " Consider what information a new carer would need to know. More detailed"
            " information would be recorded in forms, such as 'This is me' form for"
            " dementia patients. Also includes educational history."
        )
    )


class AdmissionDetails(BaseModel):
    reason_for_admission: str = Field(
        description=(
            "The main reason why the patient was admitted to hospital, eg chest pain,"
            " breathlessness, collapse, etc."
        )
    )
    admission_method: str = Field(
        description="May be autopopulated, eg elective/emergency"
    )
    relevant_past_medical_and_mental_health_history: str = Field(
        description=(
            "Whilst the GP is likely to hold this information it is useful for"
            " documents to stand-alone and provides an insight into the basis for"
            " clinical decisions. Includes relevant previous diagnoses, problems and"
            " issues, procedures, investigations, specific anaesthesia issues, etc"
        )
    )


class Diagnoses(BaseModel):
    """List brief factual information"""

    primary_diagnosis: str = Field(
        description=(
            "Confirmed primary diagnosis (or symptoms); active dianosis being treated."
            " Record to highest level of certainty, eg do not record a diagnosis if it"
            " is not certain, record a symptom instead."
        )
    )
    secondary_diagnoses: List[str] = Field(
        description=(
            "Record any other diagnoses relevant to admission, such as: other"
            " conditions which impact on the treatment eg dementia, diabetes, COPD; "
            " complications during admission eg venous thromboembolism, hospital"
            " acquired pneumonia; or incidental new diagnoses."
        )
    )


class ClinicalSummary(BaseModel):
    clinical_summary: str = Field(
        description=(
            "Details of the patient's journey can be written in this section, including"
            " details about the patient's admission and response to treatments,"
            " recorded as a summary narrative. Very concise, where possible."
        )
    )
    procedures: List[str] = Field(
        description=(
            "The details of any therapeutic or diagnostic procedures performed. This"
            " should be the name of the procedure, with additional comments if needed."
        )
    )
    investigation_results: List[str] = Field(
        description=(
            "It is important to include results of investigations which the GP is"
            " likely to monitor either of the health condition or associated with"
            " medication use eg renal function in patients with diabetes or prescribed"
            " an ACE inhibitor. This is also an opportunity to provide more detail on"
            " medical problems not related to the main admission eg current lung"
            " function tests in patient with COPD admission for elective procedure;"
            " cardiac echogram, etc"
        )
    )


class DischargeDetailsAndPlan(BaseModel):
    discharge_destination: str = Field(
        "Highlight when different to patient's usual address and if permanent or"
        " interim arrangement eg residential care, rehabilitation facility, local"
        " hospital (from tertiary centre)"
    )


class PlanAndRequestedActions(BaseModel):
    plan_and_requested_actions: str = Field(
        description=(
            "Make clear where the responsibility for actions lies (eg with the GP"
            " practice or hospital). eg Health or test monitoring, specialist services"
            " eg Macmillan, Diabetes, Optometry"
        )
    )
    information_and_advice_given: str = Field(
        description=(
            "Note of information and advice given and patient/carer comprehension"
        )
    )
    patient_and_carer_concerns_expectations_and_wishes: str = Field(
        description=(
            "Description of the concerns, wishes or goals of the person in relation to"
            " their care, as expressed by the person, their representative or carer."
            " Also record who has expressed these. Where the person lacks capacity this"
            " may include their representative's concerns, expectations or wishes."
        )
    )
    next_appointment_details: str = Field(
        description=(
            "Follow-up appointment booked, eg outpatient department - include contact"
            " details."
        )
    )


class AllergiesAndAdverseReaction(BaseModel):
    causative_agent: str = Field(
        description=(
            "The agent such as food, drug or substances that has caused or may cause an"
            " allergy intolerance or adverse reaction in this patient."
        )
    )
    description_of_reaction: str = Field(
        description=(
            "A description of the manifestation of the allergic reaction experienced by"
            " the patient. Eg skin rash."
        )
    )


class RCPGuidelines(BaseModel):
    """The discharge summary should be brief, containing only pertinent information on the
    hospital episode, rather than duplicating information which GPs already have access to in their own records.
    """

    patient_demographics: PatientDemographics
    # GP practice not included in example so not included here
    social_context: SocialContext
    admission_details: AdmissionDetails
    diagnoses: Diagnoses
    clinical_summary: ClinicalSummary
    discharge_details: DischargeDetailsAndPlan
    plan_and_requested_actions: PlanAndRequestedActions
    allergies_and_adverse_reaction: List[AllergiesAndAdverseReaction]
