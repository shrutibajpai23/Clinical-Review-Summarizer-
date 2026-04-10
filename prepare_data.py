"""
Root-level script: converts mtsamples.csv → individual .txt files in data/raw/
Run: python prepare_data.py
"""

import os
import re
import pandas as pd
from pathlib import Path

# ── Config
CSV_PATH    = "Data/mtsamples.csv"
RAW_DIR     = Path("data/raw")
DEV_LIMIT   = 20          


def sanitize_filename(text: str, max_len: int = 40) -> str:
    """Turn arbitrary text into a safe filename fragment."""
    text = re.sub(r"[^\w\s-]", "", text or "")
    text = re.sub(r"\s+", "_", text.strip())
    return text[:max_len]


def safe_str(val, default: str = "") -> str:
    """Convert a value to string safely, handling NaN/float from pandas."""
    if val is None or (isinstance(val, float)):
        return default
    return str(val).strip()


def build_file_content(row: pd.Series) -> str:
    """Combine all relevant columns into a single readable text block."""
    parts = [
        f"SPECIALTY: {safe_str(row.get('medical_specialty'), 'Unknown')}",
        f"SAMPLE NAME: {safe_str(row.get('sample_name'), 'Unknown')}",
        f"DESCRIPTION: {safe_str(row.get('description'))}",
        f"KEYWORDS: {safe_str(row.get('keywords'))}",
        "",
        "TRANSCRIPTION:",
        str(row.get("transcription", "")).strip(),
    ]
    return "\n".join(parts)


def prepare(limit: int | None = DEV_LIMIT) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CSV_PATH)
    print(f"✅ Loaded CSV: {len(df)} rows, columns: {list(df.columns)}")

    if limit:
        df = df.head(limit)
        print(f"⚠️  Dev mode — processing first {limit} rows")

    saved, skipped = 0, 0

    for idx, row in df.iterrows():
        transcription = str(row.get("transcription", "")).strip()
        if not transcription or transcription.lower() == "nan":
            skipped += 1
            continue

        specialty   = sanitize_filename(row.get("medical_specialty", "Unknown"))
        sample_name = sanitize_filename(row.get("sample_name", f"sample_{idx}"))

        # zero-padded index keeps filenames sortable
        filename = f"{str(idx).zfill(4)}_{specialty}_{sample_name}.txt"
        file_path = RAW_DIR / filename

        content = build_file_content(row)
        file_path.write_text(content, encoding="utf-8")
        saved += 1

    print(f"\n✅ Done — saved: {saved} files | skipped (empty): {skipped}")
    print(f"📁 Output directory: {RAW_DIR.resolve()}")


if __name__ == "__main__":
    prepare()