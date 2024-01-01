import re


def clean_text(text: str | None) -> str:
    if not text:
        return ""

    return re.sub(r"\s+", " ", text).strip()
