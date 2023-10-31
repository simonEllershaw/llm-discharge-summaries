from typing import List

from discharge_summaries.schemas.prsb_guidelines import GPPractice


class GPPracticeWriter:
    def run(self, physician_notes: List[str]) -> GPPractice:
        return GPPractice(
            gp_name="",
            gp_practice_details="",
            gp_practice_identifier="",
        )
