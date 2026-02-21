from pathlib import Path


def save_text(text: str, path: str = "output.txt") -> None:
    Path(path).write_text(text, encoding="utf-8")
