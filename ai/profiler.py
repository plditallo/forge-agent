import pandas as pd
import json
from pathlib import Path


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def profile_file(file_path: str) -> dict:
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}. Supported: {SUPPORTED_EXTENSIONS}")

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

        # Sample values - first 3 non-null
        sample_values = series.dropna().head(3).tolist()
        col_info["sample_values"] = [str(v) for v in sample_values]

        # Basic type classification
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

        # PII signal detection
        col_lower = col.lower()
        pii_signals = [
            "name", "email", "phone", "address", "ssn", "social",
            "dob", "birth", "zip", "postal", "gender", "race",
            "salary", "income", "credit", "account", "password"
        ]
        col_info["pii_signal"] = any(signal in col_lower for signal in pii_signals)

        columns.append(col_info)

    # Overall completeness
    total_cells = row_count * col_count
    total_nulls = sum(c["null_count"] for c in columns)
    completeness = round(1 - (total_nulls / total_cells), 4) if total_cells > 0 else 0

    # Duplicate row rate
    duplicate_count = int(df.duplicated().sum())
    duplicate_rate = round(duplicate_count / row_count, 4) if row_count > 0 else 0

    # PII flag
    pii_columns = [c["name"] for c in columns if c["pii_signal"]]

    profile = {
        "file_name": file_name,
        "file_type": file_type,
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