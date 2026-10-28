from pathlib import Path
import pandas as pd
from medcat.cat import CAT

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
ANNOTATED_DIR = OUTPUT_DIR / "annotators_eval"
CONCEPT_COUNT_DIR = OUTPUT_DIR / "concept_count"
MODEL_PACK_PATH = BASE_DIR / "models" / "v2_Snomed2025_MIMIC_IV_bbe806e192df009f.zip"

ERROR_COLUMNS = [
    "Missed- Severe",
    "Missed- Minor",
    "Added- Hallucination",
    "Added- Not relevant",
]


def load_clinical_summaries() -> pd.DataFrame:
    """Loads unique clinical summaries from the annotated outputs."""
    eval_dfs = []
    for annotator_dir in ANNOTATED_DIR.iterdir():
        if not annotator_dir.is_dir():
            continue

        for hadm_id_dir in annotator_dir.iterdir():
            if not hadm_id_dir.is_dir():
                continue

            excel_path = hadm_id_dir / f"discharge_summary_{hadm_id_dir.stem}.xlsx"
            if not excel_path.exists():
                continue

            df = pd.read_excel(excel_path, engine="openpyxl", header=1)
            eval_dfs.append(df[df["Field"] == "Clinical Summary"])

    clinical_summaries = pd.concat(eval_dfs)
    clinical_summaries[ERROR_COLUMNS] = clinical_summaries[ERROR_COLUMNS].fillna(0)
    return clinical_summaries


def format_median_iqr(series: pd.Series) -> str:
    """Formats a pandas Series as Median [Q1 - Q3]."""
    median = series.median()
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    return f"{median:.2f} [{q1:.2f} - {q3:.2f}]"


def compute_metrics_table(clinical_summaries: pd.DataFrame) -> pd.DataFrame:
    """Computes evaluation metrics using sentences vs SNOMED concepts as predicted positives."""
    total_fp = (
        clinical_summaries["Added- Hallucination"] + clinical_summaries["Added- Not relevant"]
    ).sum()
    total_fn = (
        clinical_summaries["Missed- Severe"] + clinical_summaries["Missed- Minor"]
    ).sum()

    rows = []
    for method, col in [("Sentence extraction", "Sentence Count"), ("Snowmed extraction", "SNOMED Count")]:
        positives_series = clinical_summaries[col]
        total_positives = positives_series.sum()
        total_tp = total_positives - total_fp
        recall = total_tp / (total_tp + total_fn)
        precision = total_tp / total_positives
        f1 = 2 * (precision * recall) / (precision + recall)
        rows.append({
            "Positive Predictions": format_median_iqr(positives_series),
            "Recall": recall,
            "Precision": precision,
            "F1": f1,
        })

    return pd.DataFrame(rows, index=["Sentence extraction", "Snowmed extraction"])


if __name__ == "__main__":
    clinical_summaries = load_clinical_summaries()
    print(f"Number of clinical summaries: {len(clinical_summaries)}")

    print("Loading model pack...")
    cat = CAT.load_model_pack(str(MODEL_PACK_PATH))
    print("Model pack loaded.")

    print("Calculating number of sentences per summary...")
    clinical_summaries["Sentence Count"] = [
        len(text.split(". ")) for text in clinical_summaries["Value"]
    ]

    print("Calculating number of SNOMED concepts per summary...")
    clinical_summaries["SNOMED Count"] = [
        len(set(entity["cui"] for entity in cat.get_entities(text).get("entities", {}).values()))
        for text in clinical_summaries["Value"]
    ]

    print(f"Average number of sentences per summary: {clinical_summaries['Sentence Count'].mean():.3f}")
    print(f"Average number of SNOMED concepts per summary: {clinical_summaries['SNOMED Count'].mean():.3f}")

    metrics_df = compute_metrics_table(clinical_summaries)
    print("\nMetrics Table:")
    print(metrics_df)

    CONCEPT_COUNT_DIR.mkdir(parents=True, exist_ok=True)
    (CONCEPT_COUNT_DIR / "table.md").write_text(metrics_df.to_markdown(floatfmt=".3f"))
    (CONCEPT_COUNT_DIR / "table.tex").write_text(metrics_df.to_latex(float_format="%.3f"))

    print(f"\nOutputs written to:\n - {CONCEPT_COUNT_DIR / 'table.md'}\n - {CONCEPT_COUNT_DIR / 'table.tex'}")
