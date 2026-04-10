"""
Clean raw text and detect the clinical document type.
"""

from __future__ import annotations

import re
import unicodedata


#Text cleaning

def clean_text(text: str) -> str:
    """
    Normalise raw clinical text for downstream embedding and chunking.

    Steps
    -----
    1. Unicode normalisation (NFKC)
    2. Replace common encoding artifacts (smart quotes, dashes, etc.)
    3. Strip boilerplate headers / footers that add noise
    4. Collapse excessive whitespace
    5. Remove null bytes and non-printable control characters
    """
    if not text:
        return ""

    
    text = unicodedata.normalize("NFKC", text)

    
    replacements = {
        "\u2018": "'", "\u2019": "'",   
        "\u201c": '"', "\u201d": '"',   
        "\u2013": "-", "\u2014": "-",   
        "\u2022": "*",                  
        "\u00a0": " ",                  
        "\ufffd": "",                   
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    text = re.sub(r"[^\x09\x0a\x20-\x7e\x80-\xff]", " ", text)

    text = re.sub(r"\n{3,}", "\n\n", text)

    text = re.sub(r"[ \t]{2,}", " ", text)

    lines = [line.strip() for line in text.splitlines()]
    text  = "\n".join(lines).strip()

    return text


# Document type detection 

_DOC_TYPE_PATTERNS: list[tuple[str, list[str]]] = [
    (
        "discharge_summary",
        [
            r"\bdischarge\s+summary\b",
            r"\bdischarge\s+diagnosis\b",
            r"\badmission\s+date\b",
            r"\bdischarge\s+date\b",
            r"\bhospital\s+course\b",
        ],
    ),
    (
        "clinical_trial",
        [
            r"\bclinical\s+trial\b",
            r"\brandomized\b",
            r"\bplacebo\b",
            r"\bcontrol\s+group\b",
            r"\bstudy\s+protocol\b",
            r"\binclusion\s+criteria\b",
        ],
    ),
    (
        "research_paper",
        [
            r"\babstract\b",
            r"\bintroduction\b",
            r"\bmethods\b",
            r"\bresults\b",
            r"\bconclusion\b",
            r"\breferences\b",
            r"\bdoi\b",
            r"\bjournal\b",
        ],
    ),
    (
        "doctor_note",
        [
            r"\bchief\s+complaint\b",
            r"\bhistory\s+of\s+present\s+illness\b",
            r"\bhpi\b",
            r"\bphysical\s+exam\b",
            r"\bassessment\s+and\s+plan\b",
            r"\bsubjective\b",
            r"\bobjective\b",
            r"\bplan\b",
            r"\bsoap\b",
            r"\bfollow.?up\b",
        ],
    ),
]


def detect_doc_type(filename: str, text_preview: str) -> str:
    """
    Classify a clinical document into one of five types.

    Classification is rule-based on keyword patterns found in the
    filename and the first ~1000 characters of the text.

    Returns
    -------
    One of:
        discharge_summary | clinical_trial | research_paper |
        doctor_note       | general_clinical
    """
    combined = (filename + " " + text_preview[:1000]).lower()

    scores: dict[str, int] = {}
    for doc_type, patterns in _DOC_TYPE_PATTERNS:
        hits = sum(1 for p in patterns if re.search(p, combined))
        if hits:
            scores[doc_type] = hits

    if scores:
        return max(scores, key=scores.get)   # type: ignore[arg-type]

    return "general_clinical"



if __name__ == "__main__":
    sample = """
    CHIEF COMPLAINT:  Shortness of breath.
    HISTORY OF PRESENT ILLNESS:  Patient  is a  68-year-old male…
    PHYSICAL EXAM:  Vitals — BP 140/90, HR 88.
    ASSESSMENT AND PLAN:  Hypertension — continue current meds.
    """
    cleaned = clean_text(sample)
    doc_type = detect_doc_type("0001_Cardiology_note.txt", cleaned)
    print("Cleaned text:\n", cleaned[:200])
    print("\nDetected type:", doc_type)