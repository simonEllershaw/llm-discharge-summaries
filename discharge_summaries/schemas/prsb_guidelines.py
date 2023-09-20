from typing import Any, Dict, List, Optional, Set, Type, Union

from pydantic import BaseModel, Field


class PatientDemographics(BaseModel):
    patient_name: str = Field(description="The full name of the patient")
    patient_preferred_name: str = Field(
        description="The name by which a patient wishes to be addressed."
    )
    date_of_birth: str = Field(description="The date of birth of the patient.")
    gender: str = Field(
        description="The patient's gender. As the patient wishes to portray themselves."
    )
    nhs_number: str = Field(
        description=(
            "The unique identifier for a patient within the NHS in England and Wales."
        )
    )
    other_identifier: str = Field(
        description=(
            "Country specific or local identifier, e.g., Community Health Index (CHI)"
            " in Scotland. Two data items: type of identifier and identifier."
        )
    )
    patient_address: str = Field(description="Patient's usual place of residence.")
    patient_email_address: str = Field(description="Email address of the patient")
    patient_telephone_number: str = Field(
        description=(
            "Telephone contact details of the patient. To include, e.g., mobile, work"
            " and home number if available."
        )
    )
    relevant_contacts: str = Field(
        description=(
            "Include the most important contacts including:*Personal contacts e.g.,"
            " next of kin, in case of emergency contact, lasting power of attorney,"
            " dependants, informal carers etc.*Health/care professional contacts e.g.,"
            " social worker, hospital clinician, care coordinator, Independent Mental"
            " Capacity Advocate (IMCA) etc.Name, relationship, role (if formal role),"
            " contact details and availability, eg out of hours."
        )
    )


class GPPractice(BaseModel):
    gp_name: str = Field(
        description=(
            "Where the patient or patient's representative offers the name of a GP as"
            " their usual GP"
        )
    )
    gp_practice_details: str = Field(
        description="Name and address of the patient's registered GP Practice"
    )
    gp_practice_identifier: str = Field(
        description="The identifier of the registered GP Practice."
    )


class ReferrerDetails(BaseModel):
    referrer_details: str = Field(
        description=(
            "Name, role, grade, organisation and contact details of referrer. If not an"
            " individual, this could be e.g. GP surgery, department, specialty,"
            " sub-specialty, educational institution, mental health team etc. Also"
            " needs to include self-referral."
        )
    )


class SocialContext(BaseModel):
    household_composition: str = Field(
        description=(
            "E.g., lives alone, lives with family, lives with partner, etc. This may be"
            " free text."
        )
    )
    occupational_history: List[str] = Field(
        description=(
            "The current and/or previous relevant occupation(s) of the"
            " patient/individual."
        )
    )
    educational_history: str = Field(
        description=(
            "The current and/or previous relevant educational history of the"
            " patient/individual"
        )
    )


class IndividualRequirement(BaseModel):
    individual_requirement: str = Field(
        description=(
            "Individual requirement that a person has. These may be a communication,"
            " cultural, cognitive or mobility need."
        )
    )


class ParticipationInResearch(BaseModel):
    name_of_research_study: str = Field(
        description="Name of the research study/trial and/or drug/intervention"
    )


class AdmissionDetails(BaseModel):
    reason_for_admission: str = Field(
        description=(
            "The health problems and issues experienced by the patient that prompted"
            " the decision to admit to hospital e.g. chest pain, mental health crisis,"
            " blackout, fall, a specific procedure, intervention, investigation or"
            " treatment, non compliance with treatment."
        )
    )
    admission_method: str = Field(
        description=(
            "How the patient was admitted to hospital. For example: elective,"
            " emergency, maternity, transfer etc."
        )
    )
    source_of_admission: str = Field(
        description=(
            "Where the patient was immediately prior to admission, e.g. usual place of"
            " residence, temporary place of residence, penal establishment. National"
            " code."
        )
    )
    date_time_of_admission: str = Field(
        description="Date and time patient admitted to hospital."
    )


class DischargeDetails(BaseModel):
    discharging_consultant: str = Field(
        description="The consultant responsible for the patient at time of discharge"
    )
    discharging_speciality_or_department: str = Field(
        description=(
            "The specialty or department responsible for the patient at the time of"
            " discharge"
        )
    )
    discharge_location: str = Field(
        description="The ward or unit the patient was in immediately prior to discharge"
    )
    date_time_of_discharge: str = Field(description="The actual date of discharge")
    discharge_method: str = Field(
        description=(
            "The method of discharge from hospital. National codes: e.g.. patient"
            " discharged on clinical advice or with clinical consent; patient"
            " discharged him/herself or was discharged by a relative or advocate;"
            " patient died; stillbirth"
        )
    )
    discharge_destination_cluster: str = Field(
        description=(
            "The destination of the patient on discharge. National codes. Eg, High"
            " Dependency Unit."
        )
    )
    discharge_type: str = Field(
        description=(
            "The destination of the patient on discharge from hospital. National codes"
            " e.g.. NHS-run care home."
        )
    )
    discharge_address: str = Field(
        description=(
            "Address to which patient discharged. Only complete where this is not the"
            " usual place of residence."
        )
    )


class Diagnosis(BaseModel):
    diagnosis_name: str = Field(
        description="Confirmed diagnosis (or symptom); active diagnosis being treated."
    )
    diagnosis_stage: str = Field(description="Stage of the disease, where relevant.")
    comment: str = Field(
        description=(
            "Supporting text may be given covering diagnosis confirmation, active"
            " diagnosis being treated."
        )
    )


class Procedure(BaseModel):
    procedure_name: str = Field(
        description="The therapeutic or diagnostic procedure performed."
    )
    anatomical_site: str = Field(description="The body site of the procedure")
    laterality: str = Field(description="Laterality of the procedure")
    complications_related_to_procedure: List[str] = Field(
        description=(
            "Details of any intra-operative complications encountered during the"
            " procedure, arising during the patient's stay in the recovery unit or"
            " directly attributable to the procedure."
        )
    )
    specific_anaesthesia_issues: List[str] = Field(
        description=(
            "Details of any adverse reaction to any anaesthetic agents including local"
            " anaesthesia. Problematic intubation, transfusion reaction, etc."
        )
    )
    comment: str = Field(
        description=(
            "Any further textual comment to clarify such as statement that information"
            " is partial or incomplete."
        )
    )


class ClinicalSummary(BaseModel):
    clinical_summary: str = Field(
        description=(
            "Summary of the encounter. Where possible, very brief. This may include"
            " interpretation of findings and results; differential diagnoses, opinion"
            " and specific action(s). Planned actions will be recorded under 'plan'."
        )
    )


class InvestigationResult(BaseModel):
    investigation_result: str = Field(
        description=(
            "For each investigation, the result of the investigation (this includes the"
            " result value, with unit of observation and reference interval where"
            " applicable and date, and plans for acting upon investigation results."
        )
    )


class AssessmentScale(BaseModel):
    assessment_scale: str = Field(
        description=(
            "Assessment scale used, eg New York Heart Failure, Activities of Daily"
            " Living (ADL)"
        )
    )


class LegalInformation(BaseModel):
    consent_for_treatment_record: str = Field(
        description=(
            "Whether consent has been obtained for the treatment. May include where"
            " record of consent is located or record of consent."
        )
    )
    consent_for_information_sharing: str = Field(
        description=(
            "Whether consent has been obtained for the treatment. May include where"
            " record of consent is located or record of consent."
        )
    )
    consent_relation_to_child: str = Field(
        description=(
            "Consideration of age and competency. Record of person with parental"
            " responsibility or appointed guardian where child lacks competency."
        )
    )
    mental_capacity_assessment: str = Field(
        description=(
            "Whether an assessment of the mental capacity of the (adult) person has"
            " been undertaken, if so, what capacity the decision relates to, who"
            " carried it out, when and the outcome of the assessment. Also record best"
            " interests decision if person lacks capacity."
        )
    )
    advance_decision_to_refuse_treatment: str = Field(
        description=(
            "A record of an advance decision to refuse one or more specific types of"
            " future treatment, made by a person who had capacity at the time of"
            " recording the decision. The decision only applies when the person no"
            " longer has the capacity to consent to or refuse the specific treatment"
            " being considered. An ADRT must be in writing, signed and witnessed. If"
            " the ADRT is refusing life-sustaining treatment it must state specifically"
            " that the treatment is refused even if the person's life is at risk."
        )
    )
    lasting_power_of_attorney_for_personal_wealfare_or_court_appointed_deputy: str = Field(
        description=(
            "Record of one or more people who have been given power (LPA) by the person"
            " when they had capacity to make decisions about their health and welfare"
            " should they lose capacity to make those decisions. To be valid, an LPA"
            " must have been registered with the Court of Protection. If"
            " life-sustaining treatment is being considered the LPA document must state"
            " specifically that the attorney has been given power to consent to or"
            " refuse life-sustaining treatment. Details of any person (deputy)"
            " appointed by the court to make decisions about the person's health and"
            " welfare. A deputy does not have the power to refuse life-sustaining"
            " treatment."
        )
    )
    organ_and_tissue_donation: str = Field(
        description=(
            "Whether the person has given consent for organ and/or tissue donation or"
            " opted out of automatic donation where applicable. The location of the"
            " relevant information/documents."
        )
    )
    safeguarding_issues: str = Field(
        description=(
            "Any legal matters relating to safeguarding of a vulnerable child or adult,"
            " e.g., child protection plan, protection of vulnerable adult."
        )
    )


class SafetyAlerts(BaseModel):
    risk_to_self: str = Field(
        description=(
            "Risks the patient poses to themselves, e.g., suicide, overdose, self-harm,"
            " self-neglect."
        )
    )
    risk_to_others: str = Field(
        description=(
            "Risks the patient poses to themselves, e.g., suicide, overdose, self-harm,"
            " self-neglect."
        )
    )
    risk_from_others: str = Field(
        description=(
            "Details of where an adult or child is at risk from an identified person"
            " e.g. family member etc."
        )
    )


class StructuredDoseTiming(BaseModel):
    dose_direction_duration: str = Field(
        description=(
            "Recommendation of the time period for which the medication should be"
            " continued, including direction not to discontinue."
        )
    )
    additional_instruction: str = Field(
        description=(
            "Additional multiple dosage or administration instructions as plain text."
            " This may include guidance to the prescriber, patient or person"
            " administering the medication. In some settings, specific Administration"
            ' Instructions may be re-labelled as "Patient advice" or "Dispensing'
            ' Instruction" to capture these flavours of instruction. Comment: e.g.'
            ' “Omit morning dose on day of procedure”, "for pain or fever", "Dispense'
            ' weekly".'
        )
    )


class StructuredDoseDirection(BaseModel):
    structured_dose_amount: str = Field(
        description=(
            "A structural representation of dose amount.Comment: e.g. 20mg or 2 tablets"
            " This element will generally only be used when persisting data within"
            " systems with 'Parsable dose directions' being used to exchange the same"
            " information between systems."
        )
    )
    structured_dose_timing: StructuredDoseTiming = Field(
        description=(
            "A structural, computable representation of dose timing and maximum dose."
        )
    )


class CourseDetails(BaseModel):
    course_status: str = Field(
        description=(
            "The status of this prescription in an ambulatory (outpatient/GP/community)"
            " context"
        )
    )
    start_date_time: str = Field(
        description=(
            "The status of this prescription in an ambulatory (outpatient/GP/community)"
            " context"
        )
    )
    end_date_time: str = Field(
        description="The date and/or time that the medication course should finish."
    )
    indication: str = Field(
        description="Reason for medication being prescribed, where known."
    )
    link_to_indication_record: str = Field(
        description=(
            "A link to the record which contains the Indication for this medication"
            " order."
        )
    )
    comment_recommendation: str = Field(
        description=(
            "Suggestions about duration and/or review, ongoing monitoring requirements,"
            " advice on starting, discontinuing or changing medication."
        )
    )


class MedicationChangeSummary(BaseModel):
    status: str = Field(
        description="The nature of any change made to the medication since admission."
    )
    indication: str = Field(
        description=(
            "Reason for change in medication, eg sub-therapeutic dose, patient"
            " intolerant."
        )
    )
    date_of_latest_change: str = Field(
        description="The date of the latest change - addition, or amendment"
    )
    description_of_amendment: str = Field(
        description=(
            "Where a change is made to the medication ie one drug stopped and another"
            " started or eg dose, frequency or route is changed."
        )
    )


class MedicationItem(BaseModel):
    medication_name: str = Field(
        description=(
            "May be generic name or brand name (as appropriate).Mandatory medication"
            " name coded using a SNOMED CT/dm+d term where possible, allowing plain"
            " text for historical/patient reported items , extemporaneous preparations"
            " or those not registered in dm+d. Comment: e.g.“Citalopram tab 20mg”,"
            ' "Trimethoprim"'
        )
    )
    form: str = Field(
        description=(
            "Form of the medicinal substance e.g capsules, tablets, liquid. Not"
            " normally required unless a specific form has been requested by the"
            ' prescriber. Comment: e.g. "Modified Release Capsules"'
        )
    )
    quantity_supplied: str = Field(
        description=(
            "The quantity of the medication (eg tablets, inhalers, etc.) provided to"
            " the patient on discharge. This may be dispensed by the pharmacy or on the"
            " ward."
        )
    )
    route: str = Field(
        description=(
            "Medication administration description (oral, IM, IV, etc.): may include"
            " method of administration, (e.g., by infusion, via nebuliser, via NG"
            " tube).Optional medication route, using SNOMED CT terms where possible."
            " Not generally applicable to product-based medication. Should not be used"
            " to specify a specific administration site, for which a separate archetype"
            ' is used e.g. The Route is "intraocular" the  Site may be "Left eye".'
            ' Comment: e.g. "Oral", "Intraocular". Note that this element'
            " supportsmultiple Routes to allow a choice to be specified by the"
            " prescriber"
        )
    )
    site: str = Field(
        description=(
            "The anatomical site at which the medication is to be administered."
            ' Comment: e.g. "Left eye"'
        )
    )
    method: str = Field(
        description=(
            "The technique or method by which the medication is to be administered."
        )
    )
    dose_directions_description: str = Field(
        description=(
            "A single plain text phrase describing the entire medication dosage and"
            " administration directions, including dose quantity and medication"
            " frequency.Comment: e.g. “I tablet at night” or “20mg at 10pm” This is the"
            " form of dosage direction text normally available from UK GP systems."
        )
    )
    dose_amount_description: str = Field(
        description=(
            "A plain text description of medication single dose amount, as described in"
            ' the AoMRC medication headings.Comment: e.g. "30 mg" or "2 tabs". UK'
            " Secondary care clinicians and systems normally minimally structure their"
            " dose directions, separating Dose amount and Dose timing (often referred"
            " to as Dose and Frequency). This format is not normally used in GP"
            " systems, which will always import Dose and Frequency descriptions"
            " concatenated into the single Dose directions description."
        )
    )
    dose_timing_description: str = Field(
        description=(
            "A plain text description of medication dose frequency, as described in the"
            ' AoMRC medication headings. Comment: e.g. "Twice a day", "At 8am 2pm and'
            ' 10pm". UK Secondary care clinicians and systems normally minimally'
            " structure their dose directions, separating Dose amount and Dose timing"
            " (often referred to as Dose and Frequency). This format is not normally"
            " used in GP systems, which will always import Dose and"
            " Frequency descriptions concatenated into the single Dose directions"
            " description"
        )
    )
    structured_dose_direction: StructuredDoseDirection
    course_details: CourseDetails = Field(
        description="Details of the overall course of medication."
    )
    medication_change_summary: MedicationChangeSummary = Field(
        description="Records the changes made to medication since admission"
    )
    total_dose_daily_quantity: str = Field(
        description=(
            "The total daily dose of this medication. This is helpful for estimating"
            " optimal adherence to dosing guidance. It may be computed from"
            " product/dose strength and frequency or entered manually."
        )
    )


class MedicalDeviceEntry(BaseModel):
    name_of_discontinued_medication: str = Field(
        description=(
            "Any therapeutic medical device of relevance that does not have"
            " representation in the NHS dictionary of medicines and medical devices"
            " (dm+d)."
        )
    )


class MedicationDiscontinued(MedicationChangeSummary):
    name_of_discontinued_medication: str = Field(
        description=(
            "Records medications / medical devices present on admission but"
            " subsequently discontinued.(This will broadly follow the same structure as"
            " the Medication change summary cluster but with addition of new data item"
            " “Name of discontinued medication” to enable this cluster to function as"
            " an entry)"
        )
    )
    comment_: str = Field(
        description="Any additional comment about the medication change."
    )


class MedicationAndMedicalDevices(BaseModel):
    medication_item_cluster: List[MedicationItem] = Field(
        description=(
            "All medications and devices that can be dm+d coded to be entered via this"
            " Medication item entryHandles details of continuation / addition /"
            " amendment of admission medicationsNB:Implementation and user guidance to"
            " make clear that any prescribable medication or medication device that has"
            " dm+d representation should be handled by this entry"
        )
    )
    medical_device_entry: List[str] = Field(
        description=(
            "Any therapeutic medical device of relevance that does not have"
            " representation in the NHS dictionary of medicines and medical devices"
            " (dm+d)."
        )
    )
    medication_discontinued_entry: List[MedicationDiscontinued] = Field(
        description=(
            "Records medications / medical devices present on admission but"
            " subsequently discontinued.(This will broadly follow the same structure as"
            " the Medication change summary cluster but with addition of new data item"
            " “Name of discontinued medication” to enable this cluster to function as"
            " an entry)"
        )
    )


class AllergyOrAdverseReaction(BaseModel):
    causative_agent: str = Field(
        description=(
            "The agent such as food, drug or substances that has caused or may cause an"
            " allergy, intolerance or adverse reaction in this patient. Or “No known"
            " drug allergies or adverse reactions” Or “Information not available”"
        )
    )
    description_of_reaction: str = Field(
        description=(
            "A description of the manifestation of the allergic or adverse reaction"
            " experienced by the patient. For example, skin rash."
        )
    )
    date_recorded: str = Field(
        description=(
            "The date that the reaction was clinically recorded/asserted. This will"
            " often equate to the date of onset of the reaction but this may not be"
            " wholly clear from source data."
        )
    )
    severity: str = Field(description="A description of the severity of the reaction")
    certainity: str = Field(
        description=(
            "A description of the certainty that the stated causative agent caused the"
            " allergic or adverse reaction."
        )
    )
    comment: str = Field(
        description=(
            "Any additional comment or clarification about the adverse reaction."
        )
    )
    type_of_reaction: str = Field(
        description=(
            "The type of reaction experienced by the patient (allergic, intolerance)"
        )
    )
    evidence: str = Field(
        description=(
            "Results of investigations that confirmed the certainty of the diagnosis."
            " Examples might include results of skin prick allergy tests"
        )
    )
    date_first_experienced: str = Field(
        description=(
            "When the reaction was first experienced. May be a date or partial date"
            " (e.g. year) or text (e.g. during childhood)"
        )
    )


class ExpectationsAndWishes(BaseModel):
    expectations_and_wishes: str = Field(
        description=(
            "Description of the concerns, wishes or goals of the person in relation to"
            " their care, as expressed by the person, their representative or carer."
            " Record who has expressed these (patient or carer/ representative on"
            " behalf of the patient).Where the person lacks capacity this may include"
            " their representative's concerns, expectations or wishes."
        )
    )
    advance_statement: str = Field(
        description=(
            "Written requests and preferences made by a person with capacity conveying"
            " their wishes, beliefs and values for their future care should they lose"
            " capacity. Include the location of the document if known."
        )
    )


class InformationAndAdviceGiven(BaseModel):
    information_and_advice_given: str = Field(
        description=(
            "Written requests and preferences made by a person with capacity conveying"
            " their wishes, beliefs and values for their future care should they lose"
            " capacity. Include the location of the document if known."
        )
    )


class PlanAndRequestedActions(BaseModel):
    actions_for_healthcare_professionals: List[str] = Field(
        description=(
            "Including planned investigations, procedures and treatment for a patient's"
            " identified conditions and priorities. For each action the following"
            " should be identified:outcome expectations, including patient's"
            " expectations"
        )
    )
    actions_for_patient_or_their_carer: List[str] = Field(
        description=(
            "For each action the following should be identified:outcome expectations,"
            " including patient's expectations."
        )
    )
    agreed_with_patient_or_legitimate_patient_representative: str = Field(
        description=(
            "Indicates whether the patient or legitimate representative has agreed the"
            " entire plan or individual aspects of treatment, expected outcomes, risks"
            " and alternative treatments."
        )
    )
    investigations_requested: List[str] = Field(
        description=(
            "Investigations requested by the clinician, including the reason for the"
            " request, the date of the request and the date of the result."
        )
    )
    procedures_requested: List[str] = Field(
        description=(
            "These are the diagnostic or therapeutic procedures that have actually been"
            " requested (and the date requested)."
        )
    )


class PersonCompletingRecord(BaseModel):
    name: str = Field(
        description=(
            "The name of the person completing the record, preferably in a structured"
            " format."
        )
    )
    role: str = Field(
        description=(
            "The role the person is playing within the organisation at the time record"
            " was updated."
        )
    )
    grade: str = Field(description="The grade of the person completing the record")
    speciality: str = Field(
        description="The main specialty of the person completing the record"
    )
    professional_identifier: str = Field(
        description=(
            "Professional identifier for the person completing the record e.g., GMC"
            " number, HCPC number etc or the personal identifier used by the local"
            " organisation."
        )
    )
    date_and_time_completed: str = Field(
        description="The date and time the record was updated."
    )
    contact_details: str = Field(
        description=(
            "Contact details of the person completing the record. For example a phone"
            " number, email address. Contact details are used to resolve queries about"
            " the record entry."
        )
    )
    organisation: str = Field(
        description="The organisation the person completing the record works for."
    )


class DistributionListRecordEntry(BaseModel):
    name: str = Field(
        description=(
            "If the communication is being sent to a named individual, then this is the"
            " name of the recipient, preferably in a structured format. An identifier"
            " for the individual, for example GMC code (for a GP), or an SDS"
            " identifier, a NHS Number (for a patient) will be sent alongside the name,"
            " but may not displayed on rendered document."
        )
    )
    role: str = Field(
        description=(
            "If the communication is being sent to either a named individual, or to a"
            " non-named person with a specific role, then this is the role of the"
            " recipient."
        )
    )
    grade: str = Field(description="The recipient's grade.")
    organisation_name: str = Field(
        description=(
            "The name of the organisation the recipient is representing or the"
            " organisation named as the receiving organisation.An identifier for the"
            " organisation will be sent alongside the name, but may not be displayed on"
            " rendered document."
        )
    )
    team: str = Field(
        description=(
            "Team that the recipient belongs to in the context of receiving this"
            " message, or the team acting as the recipient."
        )
    )
    relationship_to_subject: str = Field(
        description=(
            "The relationship of the receiver to the patient, where the receiver has a"
            " personal relationship to the patient, for example, carer or parent"
        )
    )


class SubsetPRSBGuidelines(BaseModel):
    social_context: SocialContext = Field(
        description=(
            "The social setting in which the patient lives, such as their household,"
            " occupational history, and lifestyle factors."
        ),
    )
    individual_requirements: List[IndividualRequirement] = Field(
        description=(
            " The social setting in which the patient lives, such as their household,"
            " occupational history, and lifestyle factors."
        )
    )
    participation_in_research: List[ParticipationInResearch] = Field(
        description="The details of any research studies participated in."
    )
    admission_details: AdmissionDetails = Field(
        description="Details of the patient's admission and reason for admission."
    )
    diagnoses: List[Diagnosis] = Field(description="A list of the patient's diagnoses.")
    procedures: List[Procedure] = Field(
        description="The details of any procedures performed."
    )
    clinical_summary: ClinicalSummary = Field(
        description="A brief description of the encounter."
    )
    investigation_results: List[InvestigationResult] = Field(
        description=(
            "A record of investigations and procedures requested, results and plans."
        )
    )
    assessment_scale: List[AssessmentScale] = Field(
        description="A description of any assessment scales used."
    )
    allergies_and_adverse_reactions: List[AllergyOrAdverseReaction] = Field(
        description=(
            "The details of any known allergies, intolerances or adverse reactions."
        )
    )
    expectations_and_wishes: ExpectationsAndWishes = Field(
        description=(
            "A description of the concerns, expectations or wishes of the patient."
        )
    )
    information_and_advice_given: InformationAndAdviceGiven = Field(
        description=(
            "A record of any information or advice given to the patient, carer or"
            " relevant third party."
        )
    )
    plan_and_requested_actions: PlanAndRequestedActions = Field(
        description=(
            "The details of planned investigations, procedures and treatment, and"
            " whether this plan has been agreed with the patient or their legitimate"
            " representative."
        )
    )


class PRSBGuidelines(BaseModel):
    patient_demographics: PatientDemographics = Field(
        description="Patient details and contact information.",
    )
    gp_practice: List[GPPractice] = Field(
        description="Details of the GP practice where the patient is registered."
    )
    referrer_details: ReferrerDetails = Field(
        description="Details of the individual or team who referred the patient."
    )
    social_context: SocialContext = Field(
        description=(
            "The social setting in which the patient lives, such as their household,"
            " occupational history, and lifestyle factors."
        )
    )
    individual_requirements: List[IndividualRequirement] = Field(
        description=(
            " The social setting in which the patient lives, such as their household,"
            " occupational history, and lifestyle factors."
        )
    )
    participation_in_research: List[ParticipationInResearch] = Field(
        description="The details of any research studies participated in."
    )
    admission_details: AdmissionDetails = Field(
        description="Details of the patient's admission and reason for admission."
    )
    discharge_details: DischargeDetails = Field(
        description="The details of the patient's discharge from hospital."
    )
    diagnoses: List[Diagnosis] = Field(description="A list of the patient's diagnoses.")
    procedures: List[Procedure] = Field(
        description="The details of any procedures performed."
    )
    clinical_summary: ClinicalSummary = Field(
        description="A brief description of the encounter."
    )
    investigation_results: List[InvestigationResult] = Field(
        description=(
            "A record of investigations and procedures requested, results and plans."
        )
    )
    assessment_scale: List[AssessmentScale] = Field(
        description="A description of any assessment scales used."
    )
    legal_information: LegalInformation = Field(
        description=(
            "Legal information captured relating to patient care, such as consent to"
            " treatment and mental capacity."
        )
    )
    safety_alerts: SafetyAlerts = Field(
        description=(
            "The details of any risks the patient poses to themselves or others."
        )
    )
    medications_and_medical_devices: MedicationAndMedicalDevices = Field(
        description=(
            "The details of and instructions for medications and medical equipment the"
            " patient is using."
        )
    )
    allergies_and_adverse_reactions: List[AllergyOrAdverseReaction] = Field(
        description=(
            "The details of any known allergies, intolerances or adverse reactions."
        )
    )
    expectations_and_wishes: ExpectationsAndWishes = Field(
        description=(
            "A description of the concerns, expectations or wishes of the patient."
        )
    )
    information_and_advice_given: InformationAndAdviceGiven = Field(
        description=(
            "A record of any information or advice given to the patient, carer or"
            " relevant third party."
        )
    )
    plan_and_requested_actions: PlanAndRequestedActions = Field(
        description=(
            "The details of planned investigations, procedures and treatment, and"
            " whether this plan has been agreed with the patient or their legitimate"
            " representative."
        )
    )
    person_completing_record: PersonCompletingRecord = Field(
        description="The details of the person who filled out the record."
    )
    distribution_list: List[DistributionListRecordEntry] = Field(
        description=(
            "A list of other individuals to receive a copy of this communication."
        )
    )

    class Config:
        @staticmethod
        def schema_extra(schema: Dict[str, Any], model: Type["PRSBGuidelines"]) -> None:
            schema = _remove_keys(schema, {"title", "required"})
            print(schema)


def _remove_keys(values: Any, keys_to_remove: Set[str]) -> dict:
    return (
        {
            key: _remove_keys(value, keys_to_remove)
            for key, value in values.items()
            if key not in keys_to_remove
        }
        if isinstance(values, dict)
        else values
    )


class Element(BaseModel):
    name: str
    description: str
    values: str
    snomed_codes: Optional[List[str]]


class RecordEntry(BaseModel):
    name: str
    description: str
    elements: List[Element]


class Section(BaseModel):
    name: str
    description: str
    elements: Union[List[Element], RecordEntry]
    restrict_to_last_note: bool


def section_to_json_schema(section: Section) -> dict:
    return {
        "type": "object",
        "properties": {
            section.name: {
                "type": "object",
                "description": {section.description},
                "properties": (
                    {
                        section.elements.name: {
                            "description": section.elements.description,
                            "type": "array",
                            "items": {
                                element.name: {
                                    "description": element.description,
                                    "type": "string",
                                }
                                for element in section.elements.elements
                            },
                        }
                    }
                    if type(section.elements) == RecordEntry
                    else {
                        element.name: {
                            "description": element.description,
                            "type": "string",
                        }
                        for element in section.elements
                    }
                ),
            }
        },
    }


def sections_to_json_schema(sections: List[Section]) -> dict:
    return {
        "type": "object",
        "properties": {
            section.name: {
                "type": "object",
                "description": section.description,
                "properties": (
                    {
                        section.elements.name: {
                            "description": section.elements.description,
                            "type": "array",
                            "items": {
                                element.name: {
                                    "description": element.description,
                                    "type": "string",
                                }
                                for element in section.elements.elements
                            },
                        }
                    }
                    if type(section.elements) == RecordEntry
                    else {
                        element.name: {
                            "description": element.description,
                            "type": "string",
                        }
                        for element in section.elements
                    }
                ),
            }
            for section in sections
        },
    }
