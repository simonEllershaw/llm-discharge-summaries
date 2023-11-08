from pathlib import Path
from typing import List, Set

from spacy.tokens import Span

from discharge_summaries.openai_llm.chat_models import AzureOpenAIChatModel
from discharge_summaries.openai_llm.message import Message, Role
from discharge_summaries.schemas.mimic import BHC, PhysicianNote, ProblemSection
from discharge_summaries.snomed.retriever import SnomedRetriever


class BHCWriter:
    def __init__(
        self,
        llm: AzureOpenAIChatModel,
        snomed_retriever: SnomedRetriever,
        example_bhcs: List[BHC],
        logging_dir: Path,
    ) -> None:
        self._llm = llm
        self._snomed_retriever = snomed_retriever
        self._snomed_phrase_matcher = snomed_retriever._snomed_phrase_matcher
        self._example_bhcs = example_bhcs
        self._logging_dir = logging_dir
        self._logging_dir.mkdir(exist_ok=True)
        self._message_delimiter = "\n" + ("*" * 80) + "\n"

    def _create_reason_for_admission_prompts(
        self, physician_notes: List[PhysicianNote]
    ) -> List[Message]:
        example_admission_paragraphs = "\n\n".join(
            bhc.assessment_and_plan for bhc in self._example_bhcs
        )
        return [
            Message(
                role=Role.SYSTEM,
                content=f"""You are a consultant doctor completing a medical discharge summary.
Your task is to write the first paragraph of the summary.
The paragraph should be 30 words long.
The paragraph must include the patient's:
- Age
- Gender
- Past medical history
- Reason for hospital admission
This information can be found in the admission note provided by the user.

The following are examples of first paragraphs:
{example_admission_paragraphs}""",
            ),
            Message(
                role=Role.USER,
                content=f"""Admission Note
{physician_notes[0].text}
Please write the first paragraph of the discharge summary using the admission note and the requirements given in the system message.
""",  # noqa
            ),
        ]

    def _create_finding_prompts(
        self, physician_notes: List[PhysicianNote]
    ) -> List[Message]:
        examples = "\n\n".join(
            "\n".join(
                para.heading
                for para in bhc.problem_sections
                if self._snomed_phrase_matcher(para.heading)
            )
            for bhc in self._example_bhcs
        )
        return [
            Message(
                role=Role.SYSTEM,
                content=f"""You are a consultant doctor completing a medical discharge summary.
Your task is to list the main clinical findings made during the patient's stay.
Each finding should be on a new line.
Use Snomed CT preferred terms.
This information can be found in the physician note provided by the user.

The following are examples of previous patient's clinical findings:
{examples}""",
            ),
            Message(
                role=Role.USER,
                content=f"""Physician Note
{physician_notes[-1].text}
Please write the list main clinical findings in the physician note.
""",
            ),
        ]

    @staticmethod
    def _extract_spans_to_text(extract_spans: List[Span], timestamps: List[str]) -> str:
        extract_texts = []
        for span in extract_spans:
            doc_idx = span.doc.user_data["idx"]
            extract_texts.append(
                f"Physician Note {doc_idx}, {timestamps[doc_idx]}: {span.text.strip()}"
            )
        return "\n\n".join(extract_texts)

    def _create_problem_paragraph_prompt(
        self, finding: str, extract_text: str
    ) -> List[Message]:
        examples = "\n\n".join(
            bhc.problem_sections[0].text for bhc in self._example_bhcs
        )
        return [
            Message(
                role=Role.SYSTEM,
                content=f"""You are a consultant doctor completing a medical discharge summary.
The summary is made up of multiple paragraphs focusing on different clinical findings.
Your task is to write one of these paragraphs.

The user will provide a clinical finding and a list of extracts from the physician note related
to the finding in the following format:
Clinical Finding: [Clinical finding on which to write a paragraph]
Extracts:
Physician Note [Document number], [Timestamp]: [Extract 1]
...
Physician Note [Document number], [Timestamp]: [Extract n]
These notes are ordered by time.
Only information contained in these notes may be used to write the paragraph.

Your paragraph should include the following information about the finding:
- Symptom caused by the finding
- Investigations and tests performed to diagnose the finding
- Medication prescribed for the finding
- Procedures performed to treat the finding
- Future treatment plan to manage the finding
The paragraph should be 50 words long.
Do not include other clinical findings or diagnoses in the paragraph.
Do not include the patients past medical history unless relevant to this finding.

The following are examples of clinical finding paragraphs:

{examples}""",
            ),
            Message(
                role=Role.USER,
                content=f"""Clinical Finding: {finding}
Extracts:
{extract_text}
Please write the paragraph of the discharge summary describing this clinical finding in accordance to the requirements given in the system message.
""",  # noqa
            ),
        ]

    def __call__(self, physician_notes: List[PhysicianNote], logging=True) -> BHC:
        if len({note.hadm_id for note in physician_notes}) != 1:
            raise ValueError("All physician notes must be for the same hadm_id")

        reason_for_admission_prompts = self._create_reason_for_admission_prompts(
            physician_notes
        )
        reason_for_admission_response = self._llm.query(reason_for_admission_prompts)
        if logging:
            (self._logging_dir / "reason_for_admission.txt").write_text(
                self._message_delimiter.join(
                    [message.content for message in reason_for_admission_prompts]
                    + [reason_for_admission_response.content]
                )
            )

        finding_prompts = self._create_finding_prompts(physician_notes)
        findings_response = self._llm.query(finding_prompts)
        if logging:
            (self._logging_dir / "findings.txt").write_text(
                self._message_delimiter.join(
                    [message.content for message in finding_prompts]
                    + [findings_response.content]
                )
            )

        filtered_findings: Set[str] = set()
        for finding in findings_response.content.split("\n"):
            if all(
                finding.lower() not in filtered_finding.lower()
                for filtered_finding in filtered_findings
            ):
                filtered_findings.add(finding)

        finding_to_extract_spans = self._snomed_retriever(
            [note.text for note in physician_notes], filtered_findings
        )
        timestamps = [note.timestamp for note in physician_notes]
        finding_to_extract_text = {
            finding: self._extract_spans_to_text(extract_spans, timestamps)
            for finding, extract_spans in finding_to_extract_spans.items()
        }
        problem_sections = []
        for finding, extract_text in finding_to_extract_text.items():
            problem_paragraph_prompts = self._create_problem_paragraph_prompt(
                finding, extract_text
            )
            problem_paragraph_response = self._llm.query(problem_paragraph_prompts)
            problem_sections.append(
                ProblemSection(heading=finding, text=problem_paragraph_response.content)
            )
            if logging:
                (self._logging_dir / f"problem_{finding}.txt").write_text(
                    self._message_delimiter.join(
                        [message.content for message in problem_paragraph_prompts]
                        + [problem_paragraph_response.content]
                    )
                )

        full_text = "\n\n".join(
            [reason_for_admission_response.content]
            + [
                f"{problem_section.heading}: {problem_section.text}"
                for problem_section in problem_sections
            ]
        )

        return BHC(
            hadm_id=physician_notes[0].hadm_id,
            full_text=full_text,
            assessment_and_plan=reason_for_admission_response.content,
            problem_sections=problem_sections,
        )
