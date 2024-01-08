import re


def clean_text(text: str | None) -> str:
    return re.sub(r"\s+", " ", text).strip() if text else ""
