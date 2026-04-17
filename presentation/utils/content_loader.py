"""
Content loader — reads slide files, config, and notes from disk.
"""

from pathlib import Path
import yaml


PRESENTATION_ROOT = Path(__file__).parent.parent


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_presentation_config() -> dict:
    return load_yaml(PRESENTATION_ROOT / "config" / "presentation_config.yaml")


def load_section_order() -> dict:
    return load_yaml(PRESENTATION_ROOT / "config" / "section_order.yaml")


def load_slide_file(filename: str) -> str:
    path = PRESENTATION_ROOT / "slides" / filename
    if not path.exists():
        raise FileNotFoundError(f"Slide file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_all_slides() -> list[dict]:
    """
    Returns slides in section_order sequence, each as a dict with:
    - id, file, order, group (from section_order.yaml)
    - raw_content (full file text)
    """
    section_order = load_section_order()
    slides = []
    for section in section_order["sections"]:
        try:
            raw = load_slide_file(section["file"])
            slides.append({**section, "raw_content": raw})
        except FileNotFoundError:
            slides.append({**section, "raw_content": None, "error": "File not found"})
    return slides


def load_notes_file(filename: str) -> str:
    path = PRESENTATION_ROOT / "notes" / filename
    if not path.exists():
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_speaker_notes() -> str:
    return load_notes_file("speaker_notes.md")


def load_meeting_brief() -> str:
    return load_notes_file("meeting_brief_nscc.md")
