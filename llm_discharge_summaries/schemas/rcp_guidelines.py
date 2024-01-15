from pydantic import BaseModel, Field

AUTOPOPULATED = "Autopopulated"


class PatientDemographics(BaseModel):
    patient_name: str = AUTOPOPULATED
    date_of_birth: str = AUTOPOPULATED
    patient_address: str = AUTOPOPULATED
    nhs_number: str = AUTOPOPULATED
    safety_alerts: list[str] = Field(
        description=(
            "Any alerts could be documented here eg treatment limitation decisions,"
            " multi-resistant organisms, refusal of specific managements eg blood"
            " products; safeguarding concerns. This includes risks to self (eg suicide,"
            " overdose, self-harm, neglect), to others (to carers, professionals or"
            " others) and risks from others (risk from an identified person eg family"
            " member)."
        )
    )


class GP_Practice(BaseModel):
    GP_name: str = Field(
        description=(
            "Name of a patient's general practitioner, if offered by the patient or"
            " their representative."
        )
    )
    GP_practice_details: str = AUTOPOPULATED


class SocialContext(BaseModel):
    social_context: list[str] = Field(
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
            # Additional
            "The main reason why the patient was admitted to hospital, eg chest pain,"
            " breathlessness, collapse, etc. This should be symptoms and not the"
            " diagnosis."
        )
    )
    date_time_of_admission: str = AUTOPOPULATED
    admission_method: str = Field(
        # Amended
        description="Eg elective/emergency"
    )
    relevant_past_medical_and_mental_health_history: list[str] = Field(
        description=(
            "Whilst the GP is likely to hold this information it is useful for"
            " documents to stand-alone and provides an insight into the basis for"
            " clinical decisions. Includes relevant previous diagnoses, problems and"
            " issues, procedures, investigations, specific anaesthesia issues, etc"
        )
    )


class Diagnoses(BaseModel):
    primary_diagnosis: str = Field(
        description=(
            "Confirmed primary diagnosis (or symptoms); active diagnosis being treated."
            " Record to highest level of certainty, eg do not record a diagnosis if it"
            " is not certain, record a symptom instead."
        )
    )
    secondary_diagnoses: list[str] = Field(
        description=(
            "Record any other diagnoses relevant to admission, such as: other"
            " conditions which impact on the treatment eg dementia, diabetes, COPD; "
            " complications during admission eg venous thromboembolism, hospital"
            " acquired pneumonia; or incidental new diagnoses."
            # Added
            " Do not include diagnoses made before this hospital admission."
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
    procedures: list[str] = Field(
        description=(
            "The details of any therapeutic or diagnostic procedures performed. This"
            " should be the name of the procedure, with additional comments if needed."
            # Added
            "Do not include procedures performed before this hospital admission."
        )
    )
    investigation_results: list[str] = Field(
        description=(
            "It is important to include results of investigations which the GP is"
            " likely to monitor either of the health condition or associated with"
            " medication use eg renal function in patients with diabetes or prescribed"
            " an ACE inhibitor. This is also an opportunity to provide more detail on"
            " medical problems not related to the main admission eg current lung"
            " function tests in patient with COPD admission for elective procedure,"
            " cardiac echogram "
            # Added
            ", chest x-ray, mri scan, etc. Each investigation is a separate element in"
            " the list."
        )
    )


class DischargeDetailsAndPlan(BaseModel):
    date_time_of_discharge: str = AUTOPOPULATED
    discharge_destination: str = Field(
        description=(
            "Highlight when different to patient's usual address and if permanent or"
            " interim arrangement eg residential care, rehabilitation facility, local"
            " hospital (from tertiary centre)"
        )
    )


class PlanAndRequestedActions(BaseModel):
    # Altered
    post_discharge_plan_and_requested_actions: list[str] = Field(
        description=(
            "list detailing the hospital post-discharge management plan what is"
            " expected of the GP following the patient's discharge. Make clear where"
            " the responsibility for actions lies (eg with the GP practice or"
            " hospital). eg Health or test monitoring, specialist services eg"
            " Macmillan, Diabetes, Optometry."
            # Added
            " Do not include jobs that are still to be done in hospital before"
            " discharge."
        )
    )
    information_and_advice_given: list[str] = Field(
        description=(
            "Note of information and advice given and patient/carer comprehension"
        )
    )
    patient_and_carer_concerns_expectations_and_wishes: list[str] = Field(
        description=(
            "Description of the concerns, wishes or goals of the person in relation to"
            " their care, as expressed by the person, their representative or carer."
            " Also record who has expressed these. Where the person lacks capacity this"
            " may include their representative's concerns, expectations or wishes."
        )
    )
    next_appointment_details: str = Field(
        description=(
            "Details of booked follow-up appointment. State who the appointment is with"
            " booked eg outpatient department."
            # Added
            " Note date and contact details if available."
        )
    )


class Medication(BaseModel):
    medication_name: str = Field(description="May be generic name or brand name")
    # Added field. Status definitions from PRSB guidelines
    status: str = Field(
        description=(
            "The nature of any change made to the medication since admission. Continued"
            " [Medicine present on both admission and discharge with no amendments.]."
            " Added [Medicine present on discharge but not on admission]. Amended"
            " [Medicine present on both admission and discharge but with amendment(s)"
            " since admission.]. Discontinued [The medication is no longer to be taken"
            " by the patient]"
        )
    )
    form: str = Field(
        description="Form of the medicinal substance eg capsules, tablets, liquid"
    )
    route: str = Field(
        description=(
            "Medication administration description (eg oral, intravenous, etc). May"
            " include method (eg inhaler)."
        )
    )
    dose_directions_description: str = Field(
        description=(
            "Recommendation of time period for which the medication should be"
            " continued. 'Continue indefinitely'; 'Do not discontinue' (never"
            " discontinue); 'Stop when course complete'."
        )
    )
    dose_duration_description: str = Field(
        description=(
            "Description of the entire medication dosage and administration directions,"
            " including dose quantity and medication frequency, eg '1 tablet at night'"
            " or '20mg at 10pm'"
        )
    )
    indication: str = Field(description="Reason for medication being prescribed.")
    description_of_any_amendment: str = Field(
        description="Description of any amendment, where relevant"
    )
    additional_information_patient_advice: str = Field(
        description=(
            "May include guidance to prescriber, patient or person administering the"
            " medication eg rinse mouth with water after use"
        )
    )
    quantity_supplied: str = Field(
        description=(
            "The quantity of the medication (eg tablets, inhalers, etc.) provided to"
            " the patient on discharge. This may be dispensed by the pharmacy or on the"
            " ward. Or 'Patient's own medication'."
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
    GP_practice: GP_Practice
    social_context: SocialContext
    admission_details: AdmissionDetails
    diagnoses: Diagnoses
    clinical_summary: ClinicalSummary
    discharge_details: DischargeDetailsAndPlan
    # Not included as requires inclusion of structured e-prescribing data
    # medications: list[Medication]
    plan_and_requested_actions: PlanAndRequestedActions
    allergies_and_adverse_reaction: list[AllergiesAndAdverseReaction]
