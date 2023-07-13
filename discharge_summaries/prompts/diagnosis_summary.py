from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

_system_message_template = """You are an expert medical assistant aiding a user to write a patient's discharge summary.
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
"""
_system_message_prompt = SystemMessagePromptTemplate.from_template(
    _system_message_template
)

_human_prompt_template = """Electronic Healthcare Record Extracts: {ehr_extracts}"""
_human_message_prompt = HumanMessagePromptTemplate.from_template(_human_prompt_template)

diagnosis_summary_prompt = ChatPromptTemplate.from_messages(
    [_system_message_prompt, _human_message_prompt]
)
