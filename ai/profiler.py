import pandas as pd
import json
import anthropic
from pathlib import Path


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

client = anthropic.Anthropic()

CONTENT_VALIDATION_PROMPT = """
You are a data content safety validator for FORGE Agent, a professional data certification platform.

Your job is to review a file profile (column names, sample values, and metadata) and determine whether the dataset is appropriate for a professional data marketplace.

Reject the dataset if it contains ANY of the following:
- Sexual or pornographic content in column names or sample values
- Racist, sexist, or hate speech content
- Profanity or offensive language
- Personal identifiers such as Social Security Numbers, credit card numbers, bank account numbers, or passwords
- Content that appears designed to disrupt or troll the platform (nonsense data, joke columns, etc.)
- Content that appears to be fabricated for malicious purposes

Allow the dataset if:
- It contains business, operational, scientific, or research data
- Column names and values are professional and appropriate
- PII signals like names and emails are present but acceptable (the intake form handles compliance attestation)
- Data quality is low but content is appropriate

Respond ONLY with a JSON object, no preamble, no markdown:
{
  "approved": true or false,
  "reason": "brief explanation if rejected, or 'Content approved' if approved",
  "flags": ["list of specific concerns if any, empty array if none"]
}
"""


def validate_content(file_profile: dict) -> dict:
    summary = {
        "file_name": file_profile.get("file_name"),
        "row_count": file_profile.get("row_count"),
        "column_count": file_profile.get("column_count"),
        "columns": [
            {
                "name": col["name"],
                "category": col["category"],
                "sample_values": col.get("sample_values", []),
                "pii_signal": col.get("pii_signal", False)
            }
            for col in file_profile.get("columns", [])
        ]
    }

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=500,
        system=CONTENT_VALIDATION_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Validate this dataset profile:\n{json.dumps(summary, indent=2)}"
        }]
    )

    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"approved": True, "reason": "Validation parse error — defaulting to approved", "flags": []}


def profile_file(file_path: str) -> dict:
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {SUPPORTED_EXTENSIONS}")

    # File size check
    file_size = path.stat().st_size
    if file_size > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File size {file_size / 1024 / 1024:.1f}MB exceeds the 50MB limit.")

    if ext == ".csv":
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    return build_profile(df, path.name, ext)


def build_profile(df: pd.DataFrame, file_name: str, file_type: str) -> dict:
    row_count = len(df)
    col_count = len(df.columns)

    columns = []
    for col in df.columns:
        series = df[col]
        null_count = int(series.isnull().sum())
        null_rate = round(null_count / row_count, 4) if row_count > 0 else 0
        unique_count = int(series.nunique())

        col_info = {
            "name": col,
            "dtype": str(series.dtype),
            "null_count": null_count,
            "null_rate": null_rate,
            "unique_count": unique_count,
            "unique_rate": round(unique_count / row_count, 4) if row_count > 0 else 0,
        }

        sample_values = series.dropna().head(3).tolist()
        col_info["sample_values"] = [str(v) for v in sample_values]

        if pd.api.types.is_numeric_dtype(series):
            col_info["category"] = "numeric"
            col_info["min"] = str(series.min()) if not series.empty else None
            col_info["max"] = str(series.max()) if not series.empty else None
            col_info["mean"] = str(round(series.mean(), 4)) if not series.empty else None
        elif pd.api.types.is_datetime64_any_dtype(series):
            col_info["category"] = "datetime"
            col_info["min"] = str(series.min())
            col_info["max"] = str(series.max())
        else:
            col_info["category"] = "text"

        col_lower = col.lower()
        pii_signals = [
            "name", "email", "phone", "address", "ssn", "social",
            "dob", "birth", "zip", "postal", "gender", "race",
            "salary", "income", "credit", "account", "password"
        ]
        col_info["pii_signal"] = any(signal in col_lower for signal in pii_signals)

        columns.append(col_info)

    total_cells = row_count * col_count
    total_nulls = sum(c["null_count"] for c in columns)
    completeness = round(1 - (total_nulls / total_cells), 4) if total_cells > 0 else 0
    duplicate_count = int(df.duplicated().sum())
    duplicate_rate = round(duplicate_count / row_count, 4) if row_count > 0 else 0
    pii_columns = [c["name"] for c in columns if c["pii_signal"]]

    profile = {
        "file_name": file_name,
        "file_type": file_type,
        "file_size_mb": round(0, 2),
        "row_count": row_count,
        "column_count": col_count,
        "completeness_rate": completeness,
        "duplicate_row_count": duplicate_count,
        "duplicate_row_rate": duplicate_rate,
        "pii_signals_detected": pii_columns,
        "columns": columns
    }

    return profile


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = profile_file(sys.argv[1])
        print(json.dumps(result, indent=2))
