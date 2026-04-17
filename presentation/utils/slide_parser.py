"""
Slide parser — extracts frontmatter, body sections, and flags scope drift.
"""

import re
from dataclasses import dataclass, field


SCOPE_DRIFT_PHRASES = [
    "full platform",
    "continuous monitoring",
    "deep learning engine",
    "marketplace",
]

# Section markers within slide body
SECTION_MARKERS = {
    "speaker_notes": "<!-- speaker_notes -->",
    "implementation_notes": "<!-- implementation_notes -->",
    "do_not_say": "<!-- do_not_say -->",
}


@dataclass
class ParsedSlide:
    frontmatter: dict
    body: str
    speaker_notes: str = ""
    implementation_notes: str = ""
    do_not_say: str = ""
    scope_flags: list[str] = field(default_factory=list)


def parse_frontmatter(raw: str) -> tuple[dict, str]:
    """Split YAML frontmatter from body. Returns (frontmatter_dict, body_text)."""
    import yaml

    pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
    match = pattern.match(raw)
    if match:
        fm = yaml.safe_load(match.group(1)) or {}
        body = raw[match.end():]
        return fm, body
    return {}, raw


def extract_section(text: str, marker: str) -> tuple[str, str]:
    """
    Extract a named section from slide body. Returns (section_content, remaining_body).
    Section runs from marker to the next marker or end of string.
    """
    if marker not in text:
        return "", text

    parts = text.split(marker, 1)
    before = parts[0]
    after = parts[1]

    # Check if another marker starts the next section
    next_marker_pos = len(after)
    for other_marker in SECTION_MARKERS.values():
        if other_marker in after:
            pos = after.index(other_marker)
            if pos < next_marker_pos:
                next_marker_pos = pos

    section_content = after[:next_marker_pos].strip()
    remaining_after = after[next_marker_pos:]

    return section_content, before + remaining_after


def check_scope_drift(text: str, phrases: list[str] | None = None) -> list[str]:
    """Return list of scope-drift phrases found in text (case-insensitive)."""
    phrases = phrases or SCOPE_DRIFT_PHRASES
    found = []
    lower = text.lower()
    for phrase in phrases:
        if phrase.lower() in lower:
            found.append(phrase)
    return found


def parse_slide(raw_content: str, extra_scope_phrases: list[str] | None = None) -> ParsedSlide:
    """Full parse of a slide file into a ParsedSlide dataclass."""
    if raw_content is None:
        return ParsedSlide(frontmatter={}, body="", scope_flags=["MISSING FILE"])

    frontmatter, body = parse_frontmatter(raw_content)

    # Extract special sections from body
    speaker_notes, body = extract_section(body, SECTION_MARKERS["speaker_notes"])
    implementation_notes, body = extract_section(body, SECTION_MARKERS["implementation_notes"])
    do_not_say, body = extract_section(body, SECTION_MARKERS["do_not_say"])

    # Check for scope drift in visible body only (not in notes sections)
    all_phrases = SCOPE_DRIFT_PHRASES + (extra_scope_phrases or [])
    scope_flags = check_scope_drift(body, all_phrases)

    return ParsedSlide(
        frontmatter=frontmatter,
        body=body.strip(),
        speaker_notes=speaker_notes,
        implementation_notes=implementation_notes,
        do_not_say=do_not_say,
        scope_flags=scope_flags,
    )


def parse_all_slides(raw_slides: list[dict]) -> list[dict]:
    """
    Takes the output of content_loader.load_all_slides() and adds parsed fields.
    Returns list of dicts with all original fields plus 'parsed' key.
    """
    result = []
    for slide in raw_slides:
        parsed = parse_slide(slide.get("raw_content"))
        result.append({**slide, "parsed": parsed})
    return result
