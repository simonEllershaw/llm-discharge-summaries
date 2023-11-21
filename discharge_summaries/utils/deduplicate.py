from typing import List

from discharge_summaries.schemas.mimic import PhysicianNote


def deduplicate_physician_notes(notes: List[PhysicianNote]) -> List[PhysicianNote]:
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
