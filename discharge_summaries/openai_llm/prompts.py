from discharge_summaries.openai_llm.message import Message, Role


def generate_diagnosis_summary_prompt(
    diagnosis: str, ehr_extracts: list[str]
) -> list[Message]:
    system_message = Message(
        role=Role.SYSTEM,
        content=f"""You are an expert medical assistant aiding a user to write a patient's discharge summary.
Your task is to write a paragraph on the diagnosis of the patient with {diagnosis}.
You may only use information provided by the user.
This information is in the form of extracts from the patient's medical records which explicitly mention the diagnosis.
Do not mention any diagnoses other than {diagnosis}.
Do not mention any patient history that is not directly related to {diagnosis}.
---
User messages follow the format.
Electronic Healthcare Record Extracts: $[new line separated extracts from the patient's medical records]
---
Assistant messages follow the format.
$[concise summary of information in the extracts regarding the diagnosis]
""",
    )

    ehr_extracts_str = "\n".join(ehr_extracts)
    user_message = Message(
        role=Role.USER,
        content=f"""Electronic Healthcare Record Extracts: {ehr_extracts_str}""",
    )

    return [system_message, user_message]
