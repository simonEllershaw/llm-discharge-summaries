import json
from typing import Dict, List, Tuple

from discharge_summaries.openai_llm.message import Message, Role
from discharge_summaries.schemas.mimic import PhysicianNote


def generate_diagnosis_summary_prompt(
    diagnosis: str, ehr_extracts: List[str]
) -> List[Message]:
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


def generate_bhc_paragraph_heading_extraction_prompt(
    bhc_paragraph: str, examples: List[Tuple[str, str]]
) -> List[Message]:
    PREFIX = "What is the heading of this paragraph?\n\n"

    system_message = Message(
        role=Role.SYSTEM,
        content="""You are an expert-level assistant that extracts the headings that prefix a user's paragraph.
A heading is the first 2-5 words of a paragraph that is usually separated from the main text by a colon.
You can either reply with None or an exact string match from the user text.""",
    )

    few_shot_examples = []
    for example_input, example_output in examples:
        few_shot_examples.append(
            Message(
                role=Role.USER,
                content=f"{PREFIX}{example_input}",
            )
        )
        few_shot_examples.append(
            Message(
                role=Role.ASSISTANT,
                content=example_output,
            )
        )

    user_message = Message(
        role=Role.USER,
        content=f"{PREFIX}{bhc_paragraph}",
    )

    return [system_message, *few_shot_examples, user_message]


def generate_rcp_system_message(json_schema: Dict) -> Message:
    return Message(
        role=Role.SYSTEM,
        content=f"""You are a consultant doctor tasked with writing a patients discharge summary.
A user will provide you with a list of clinical notes from a hospital stay from which you will write a discharge summary.
Each clinical note has a title of the format [Title]: [timestamp year-month-day hour:min].
Clinical notes are ordered by ascending timestamp.
Only the information in the clinical notes provided by the most recent user message can be used for this task.

The discharge summary must be written in accordance with the following json schema.
{json.dumps(json_schema)}
All fields are required.
If the relevant information is not present in the clinical notes, fields can be filled with an empty string or list.
Expand all acronyms to their full terms.""",  # noqa,
    )


def _deduplicate_physician_notes(notes: List[PhysicianNote]) -> List[PhysicianNote]:
    seen_lines = set()
    deduplicated_notes = []
    for note in notes:
        deduplicated_lines = []
        for line in note.text.split("\n"):
            if line == "" or line in seen_lines:
                pass
            else:
                seen_lines.add(line)
                deduplicated_lines.append(line)
        if deduplicated_lines:
            deduplicated_notes.append(
                note.copy(update={"text": "\n".join(deduplicated_lines)})
            )
    return deduplicated_notes


def _physician_notes_to_string(notes: List[PhysicianNote]) -> str:
    deduplicated_notes = _deduplicate_physician_notes(notes)
    deduplicated_notes = sorted(deduplicated_notes, key=lambda note: note.timestamp)
    notes_string = "\n\n".join(
        f"{note.title}: {note.timestamp}\n{note.text}" for note in deduplicated_notes
    )
    return notes_string


def generate_rcp_user_message(notes: List[PhysicianNote]) -> Message:
    return Message(
        role=Role.USER,
        content=f"""Clinical Notes
{_physician_notes_to_string(notes)}
Please write a discharge summary only using the information in this message's clinical notes.
The discharge summary must be written in accordance with the json schema given in the system message.""",
    )
