"""
Klara Greenhouse - PIVP Project Brief

Public-facing presentation surface for PIVP Tier 1 application and NSCC
conversations. Presentation mode only. No internal notes, no working mode.

v1.0.4-candidate visual system: sage/forest/ochre agtech palette, Source Serif
Pro display headers, hybrid routing/suggesting verb framing, dedicated callouts
for territory and decision-support discipline, evidence-tier badges, in-deck
PDF download for Klara Landscape v1.0.3.

Run with:
    streamlit run presentation/streamlit_app.py
"""

import re
import streamlit as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils.content_loader import load_all_slides, load_presentation_config, load_section_order
from utils.slide_parser import parse_all_slides
from utils.ui_components import (
    render_styles,
    render_slide_header,
    render_slide_body,
    render_nav_controls,
    render_landscape_pdf_download,
    ACCENT,
    TEXT_MUTED,
)


# -- Constants -----------------------------------------------------------------

LANDSCAPE_PDF_PATH = (
    Path(__file__).parent / "assets" / "landscape" / "Klara_Landscape_v1_0_3.pdf"
)
LANDSCAPE_PDF_MARKER = "<!-- LANDSCAPE_PDF_DOWNLOAD_BUTTON -->"


# -- Page config ---------------------------------------------------------------

st.set_page_config(
    page_title="Klara Greenhouse - PIVP Project Brief",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -- Load data -----------------------------------------------------------------

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


# -- Session state -------------------------------------------------------------

if "current_slide" not in st.session_state:
    st.session_state.current_slide = 0


# -- Inject styles -------------------------------------------------------------

render_styles()


# -- Sidebar -------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        f'<div style="font-family: \'Source Serif Pro\', Georgia, serif; '
        f'font-size:1.5rem;font-weight:700;color:{ACCENT};margin-bottom:0.2rem;">'
        f'Klara Greenhouse</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="font-size:0.78rem;color:{TEXT_MUTED};margin-bottom:1.5rem;'
        f'letter-spacing:0.04em;text-transform:uppercase;">PIVP Project Brief · v1.0.4-candidate</div>',
        unsafe_allow_html=True,
    )

    st.markdown("**Slides**")

    current_group = None
    for i, slide in enumerate(slides):
        group_id = slide.get("group", "")
        group_label = groups.get(group_id, group_id.replace("_", " ").title())

        if group_id != current_group:
            st.markdown(
                f'<div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.08em;'
                f'color:{ACCENT};margin-top:0.85rem;margin-bottom:0.3rem;font-weight:600;">'
                f'{group_label}</div>',
                unsafe_allow_html=True,
            )
            current_group = group_id

        parsed = slide.get("parsed")
        fm = parsed.frontmatter if parsed else {}
        title = fm.get("title", slide.get("id", f"Slide {i+1}"))
        order = slide.get("order", i + 1)

        is_active = st.session_state.current_slide == i

        if st.button(
            f"{order:02d}. {title}",
            key=f"nav_{i}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.current_slide = i
            st.rerun()


# -- Main content area ---------------------------------------------------------

current_idx = st.session_state.current_slide
slide = slides[current_idx]
parsed = slide.get("parsed")
slide_slug = slide.get("id", "")

if parsed is None:
    st.error(f"Could not load slide: {slide.get('file', 'unknown')}")
    st.stop()

fm = parsed.frontmatter
title = fm.get("title", f"Slide {current_idx + 1}")
subtitle = ""

# Extract subtitle from body (first ## line after the # title)
body_lines = parsed.body.split("\n")
cleaned_body_lines = []
skip_title = True
for line in body_lines:
    if skip_title and line.startswith("# "):
        skip_title = False
        continue
    if subtitle == "" and line.startswith("## "):
        subtitle = line.lstrip("#").strip()
        skip_title = False
        continue
    skip_title = False
    cleaned_body_lines.append(line)

body_without_title = "\n".join(cleaned_body_lines).strip()


# -- Slide header --------------------------------------------------------------

render_slide_header(title, subtitle)


# -- Slide body (with PDF-download injection point for landscape slide) -------

if slide_slug == "landscape_v103" and LANDSCAPE_PDF_MARKER in body_without_title:
    # Split body around the marker so the download button renders in the
    # exact position the slide author placed it.
    before, after = body_without_title.split(LANDSCAPE_PDF_MARKER, 1)
    render_slide_body(before)
    render_landscape_pdf_download(str(LANDSCAPE_PDF_PATH))
    render_slide_body(after)
else:
    render_slide_body(body_without_title)


# -- Navigation ----------------------------------------------------------------

st.divider()
go_prev, go_next = render_nav_controls(current_idx, len(slides))

if go_prev:
    st.session_state.current_slide = max(0, current_idx - 1)
    st.rerun()

if go_next:
    st.session_state.current_slide = min(len(slides) - 1, current_idx + 1)
    st.rerun()
