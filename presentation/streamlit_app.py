"""
Klara Greenhouse — Founder / Strategy Presentation Surface

This is NOT the end-user product. It is the founder/stakeholder/meeting deck layer
for PIVP Tier 1 application and NSCC conversations.

Run with:
    streamlit run presentation/streamlit_app.py
"""

import streamlit as st
import sys
from pathlib import Path

# Ensure utils on path when run from repo root
sys.path.insert(0, str(Path(__file__).parent))

from utils.content_loader import load_all_slides, load_presentation_config, load_section_order
from utils.slide_parser import parse_all_slides
from utils.ui_components import (
    render_styles,
    render_slide_header,
    render_slide_body,
    render_speaker_notes,
    render_do_not_say,
    render_implementation_notes,
    render_scope_flags,
    render_scope_boundary,
    render_nav_controls,
    render_mode_badge,
    ACCENT,
)


# ── Page config ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Klara Greenhouse — Founder Presentation",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Load data ─────────────────────────────────────────────────────────────────

@st.cache_data
def get_slides():
    raw = load_all_slides()
    return parse_all_slides(raw)


@st.cache_data
def get_config():
    return load_presentation_config()


@st.cache_data
def get_section_order():
    return load_section_order()


slides = get_slides()
config = get_config()
section_order = get_section_order()
groups = section_order.get("groups", {})


# ── Session state ─────────────────────────────────────────────────────────────

if "current_slide" not in st.session_state:
    st.session_state.current_slide = 0

if "view_mode" not in st.session_state:
    st.session_state.view_mode = "presentation"

if "show_speaker_notes" not in st.session_state:
    st.session_state.show_speaker_notes = False

if "show_do_not_say" not in st.session_state:
    st.session_state.show_do_not_say = False

if "show_implementation_notes" not in st.session_state:
    st.session_state.show_implementation_notes = False

if "show_scope_flags" not in st.session_state:
    st.session_state.show_scope_flags = False


# ── Inject styles ─────────────────────────────────────────────────────────────

render_styles()


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        f'<div style="font-size:1.3rem;font-weight:700;color:{ACCENT};margin-bottom:0.25rem;">Klara Greenhouse</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:0.8rem;color:#888;margin-bottom:1.5rem;">Founder Presentation</div>',
        unsafe_allow_html=True,
    )

    # Mode selector
    st.markdown("**View Mode**")
    mode_col1, mode_col2 = st.columns(2)
    with mode_col1:
        if st.button(
            "Presentation",
            use_container_width=True,
            type="primary" if st.session_state.view_mode == "presentation" else "secondary",
        ):
            st.session_state.view_mode = "presentation"
            st.session_state.show_speaker_notes = False
            st.session_state.show_do_not_say = False
            st.session_state.show_implementation_notes = False
            st.session_state.show_scope_flags = False
            st.rerun()
    with mode_col2:
        if st.button(
            "Working",
            use_container_width=True,
            type="primary" if st.session_state.view_mode == "working" else "secondary",
        ):
            st.session_state.view_mode = "working"
            st.session_state.show_speaker_notes = True
            st.session_state.show_do_not_say = True
            st.session_state.show_scope_flags = True
            st.rerun()

    st.divider()

    # Working mode toggles (only visible in working mode)
    if st.session_state.view_mode == "working":
        st.markdown("**Show in Working View**")
        st.session_state.show_speaker_notes = st.checkbox(
            "Speaker Notes", value=st.session_state.show_speaker_notes
        )
        st.session_state.show_do_not_say = st.checkbox(
            "Do Not Say", value=st.session_state.show_do_not_say
        )
        st.session_state.show_implementation_notes = st.checkbox(
            "Implementation Notes", value=st.session_state.show_implementation_notes
        )
        st.session_state.show_scope_flags = st.checkbox(
            "Scope Drift Flags", value=st.session_state.show_scope_flags
        )
        st.divider()

    # Section navigation
    st.markdown("**Slides**")

    current_group = None
    for i, slide in enumerate(slides):
        group_id = slide.get("group", "")
        group_label = groups.get(group_id, group_id.replace("_", " ").title())

        # Group header
        if group_id != current_group:
            st.markdown(
                f'<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;'
                f'color:#999;margin-top:0.75rem;margin-bottom:0.25rem;">{group_label}</div>',
                unsafe_allow_html=True,
            )
            current_group = group_id

        parsed = slide.get("parsed")
        fm = parsed.frontmatter if parsed else {}
        title = fm.get("title", slide.get("id", f"Slide {i+1}"))
        order = slide.get("order", i + 1)

        is_active = st.session_state.current_slide == i
        scope_flag = "⚠️ " if (parsed and parsed.scope_flags and st.session_state.show_scope_flags) else ""

        if st.button(
            f"{order:02d}. {scope_flag}{title}",
            key=f"nav_{i}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.current_slide = i
            st.rerun()


# ── Main content area ─────────────────────────────────────────────────────────

current_idx = st.session_state.current_slide
slide = slides[current_idx]
parsed = slide.get("parsed")

if parsed is None:
    st.error(f"Could not parse slide: {slide.get('file', 'unknown')}")
    st.stop()

fm = parsed.frontmatter
title = fm.get("title", f"Slide {current_idx + 1}")
subtitle = ""

# Extract subtitle from body (first ## line after the # title)
import re
body_lines = parsed.body.split("\n")
cleaned_body_lines = []
skip_title = True
for line in body_lines:
    if skip_title and line.startswith("# "):
        skip_title = False
        # Use the next ## as subtitle if it follows immediately
        continue
    if subtitle == "" and line.startswith("## "):
        subtitle = line.lstrip("#").strip()
        skip_title = False
        continue
    skip_title = False
    cleaned_body_lines.append(line)

body_without_title = "\n".join(cleaned_body_lines).strip()

# ── Header row ────────────────────────────────────────────────────────────────

header_col, badge_col = st.columns([5, 1])
with header_col:
    render_slide_header(title, subtitle)
with badge_col:
    st.markdown("<br>", unsafe_allow_html=True)
    render_mode_badge(st.session_state.view_mode)

# ── Scope flags (working mode only) ───────────────────────────────────────────

if st.session_state.show_scope_flags and parsed.scope_flags:
    render_scope_flags(parsed.scope_flags)

# ── Slide body ────────────────────────────────────────────────────────────────

render_slide_body(body_without_title)

# ── Scope boundary marker ─────────────────────────────────────────────────────

if fm.get("show_scope_boundary") and st.session_state.view_mode == "working":
    render_scope_boundary()

# ── Working mode annotations ──────────────────────────────────────────────────

if st.session_state.view_mode == "working":
    st.divider()

    if st.session_state.show_speaker_notes and parsed.speaker_notes:
        render_speaker_notes(parsed.speaker_notes)

    if st.session_state.show_do_not_say and parsed.do_not_say:
        render_do_not_say(parsed.do_not_say)

    if st.session_state.show_implementation_notes and parsed.implementation_notes:
        render_implementation_notes(parsed.implementation_notes)

# ── Navigation ────────────────────────────────────────────────────────────────

st.divider()
go_prev, go_next = render_nav_controls(current_idx, len(slides))

if go_prev:
    st.session_state.current_slide = max(0, current_idx - 1)
    st.rerun()

if go_next:
    st.session_state.current_slide = min(len(slides) - 1, current_idx + 1)
    st.rerun()
