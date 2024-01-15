import json

from llm_discharge_summaries.openai_llm.message import Message, Role
from llm_discharge_summaries.schemas.mimic import PhysicianNote


def generate_rcp_system_message(json_schema: dict) -> Message:
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


def _deduplicate_physician_notes(notes: list[PhysicianNote]) -> list[PhysicianNote]:
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


def _physician_notes_to_string(notes: list[PhysicianNote]) -> str:
    deduplicated_notes = _deduplicate_physician_notes(notes)
    deduplicated_notes = sorted(deduplicated_notes, key=lambda note: note.timestamp)
    notes_string = "\n\n".join(
        f"{note.title}: {note.timestamp}\n{note.text}" for note in deduplicated_notes
    )
    return notes_string


def generate_rcp_user_message(notes: list[PhysicianNote]) -> Message:
    return Message(
        role=Role.USER,
        content=f"""Clinical Notes
{_physician_notes_to_string(notes)}
Please write a discharge summary only using the information in this message's clinical notes.
The discharge summary must be written in accordance with the json schema given in the system message.""",
    )
