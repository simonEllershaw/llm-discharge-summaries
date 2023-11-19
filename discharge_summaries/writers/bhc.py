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

    def _generate_reason_for_admission(
        self, physician_notes: List[PhysicianNote], logging=True
    ) -> str:
        examples = "\n\n".join(bhc.assessment_and_plan for bhc in self._example_bhcs)

        system_message = Message(
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
{examples}""",
        )

        user_message = Message(
            role=Role.USER,
            content=f"""Admission Note
{physician_notes[0].text}
Please write the first paragraph of the discharge summary using the admission note and the requirements given in the system message.
""",  # noqa
        )

        assistant_message = self._llm.query([system_message, user_message])
        if logging:
            (self._logging_dir / "reason_for_admission.txt").write_text(
                self._message_delimiter.join(
                    [
                        message.content
                        for message in (system_message, user_message, assistant_message)
                    ]
                )
            )
        return assistant_message.content

    def _generate_findings(
        self, physician_notes: List[PhysicianNote], logging=True
    ) -> Set[str]:
        examples = "\n\n".join(
            "\n".join(
                para.heading
                for para in bhc.problem_sections
                if self._snomed_phrase_matcher(para.heading)
            )
            for bhc in self._example_bhcs
        )
        system_message = Message(
            role=Role.SYSTEM,
            content=f"""You are a consultant doctor completing a medical discharge summary.
Your task is to list the main clinical findings made during the patient's stay.
Each finding should be on a new line.
Only include previous medical conditions if they were actively managed during the patient's stay.
Use Snomed CT preferred terms.
This information can be found in the physician note provided by the user.

The following are examples of previous patient's clinical findings:
{examples}""",
        )
        user_message = Message(
            role=Role.USER,
            content=f"""Physician Note
{physician_notes[-1].text}
Please write the list main clinical findings in the physician note.
""",
        )
        assistant_message = self._llm.query([system_message, user_message])
        if logging:
            (self._logging_dir / "findings.txt").write_text(
                self._message_delimiter.join(
                    [
                        message.content
                        for message in (system_message, user_message, assistant_message)
                    ]
                )
            )

        filtered_findings: Set[str] = set()
        for finding in assistant_message.content.split("\n"):
            if all(
                finding.lower() not in filtered_finding.lower()
                for filtered_finding in filtered_findings
            ):
                filtered_findings.add(finding)

        return filtered_findings

    @staticmethod
    def _extract_spans_to_text(extract_spans: List[Span], timestamps: List[str]) -> str:
        extract_texts = []
        for span in extract_spans:
            doc_idx = span.doc.user_data["idx"]
            extract_texts.append(
                f"Physician Note {doc_idx}, {timestamps[doc_idx]}: {span.text.strip()}"
            )
        return "\n\n".join(extract_texts)

    def _generate_problem_section(
        self, finding: str, extract_text: str, logging=True
    ) -> ProblemSection:
        examples = "\n\n".join(
            bhc.problem_sections[0].text for bhc in self._example_bhcs
        )
        system_message = Message(
            role=Role.SYSTEM,
            content=f"""You are a consultant doctor completing a medical discharge summary.
The summary is made up of multiple paragraphs describing the care provided for different clinical findings.
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

Your paragraph should be brief and may include the following information (if contained in the extracts):
- Investigations or tests performed to diagnose or monitor the finding
- Medications prescribed or altered due to the finding
- Procedures performed to treat the finding
- Communication with the patient or their family about the finding
- Plans to manage the finding after discharge
Only include information that is helpful to future healthcare professionals.
Do not include other clinical findings or diagnoses in the paragraph.
Do not include the patients past medical history.

The following are examples of clinical finding paragraphs:

{examples}""",
        )
        user_message = Message(
            role=Role.USER,
            content=f"""Clinical Finding: {finding}
Extracts:
{extract_text}
Please write the paragraph of the discharge summary describing this clinical finding in accordance to the requirements given in the system message.
""",  # noqa
        )

        assistant_message = self._llm.query([system_message, user_message])
        if logging:
            (self._logging_dir / f"finding_{finding}.txt").write_text(
                self._message_delimiter.join(
                    [
                        message.content
                        for message in (system_message, user_message, assistant_message)
                    ]
                )
            )
        return ProblemSection(heading=finding, text=assistant_message.content)

    def __call__(self, physician_notes: List[PhysicianNote], logging=True) -> BHC:
        if len({note.hadm_id for note in physician_notes}) != 1:
            raise ValueError("All physician notes must be for the same hadm_id")

        reason_for_admission = self._generate_reason_for_admission(
            physician_notes, logging=True
        )

        findings = self._generate_findings(physician_notes, logging=True)
        # findings = findings.union({"Prophylaxis", "FEN", "Code", "Communication"})
        # reason_for_admission = ""
        # findings = {"Sepsis"}

        finding_to_extract_spans = self._snomed_retriever(
            [note.text for note in physician_notes], findings
        )
        timestamps = [note.timestamp for note in physician_notes]
        finding_to_extract_text = {
            finding: self._extract_spans_to_text(extract_spans, timestamps)
            for finding, extract_spans in finding_to_extract_spans.items()
            if extract_spans
        }

        problem_sections = [
            self._generate_problem_section(finding, extract_text, logging=True)
            for finding, extract_text in finding_to_extract_text.items()
        ]

        full_text = "\n\n".join(
            [reason_for_admission]
            + [
                f"{problem_section.heading}: {problem_section.text}"
                for problem_section in problem_sections
            ]
        )

        return BHC(
            hadm_id=physician_notes[0].hadm_id,
            full_text=full_text,
            assessment_and_plan=reason_for_admission,
            problem_sections=problem_sections,
        )
