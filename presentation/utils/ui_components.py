"""
UI components — reusable Streamlit rendering for the Klara presentation surface.

v1.0.4-candidate visual system:
- Sage / forest / ochre agtech palette
- Serif display headers (Source Serif Pro) + sans body
- Hybrid verb framing supported via dedicated callout components
- Mi'kma'ki territory acknowledgment uses dedicated callout treatment
- Evidence-tier badges [A][B][C][D] color-coded inline
- Section dividers with group labels
- v1.0.4-candidate update markers
"""

import streamlit as st


# ---- Palette ---------------------------------------------------------------

# Primary sage family
ACCENT = "#4A7C59"           # sage primary (matches presentation_config.yaml)
ACCENT_DEEP = "#2C5530"      # deep forest — header emphasis
ACCENT_BRIGHT = "#5C9B6B"    # brighter sage — hover/active
ACCENT_SUBTLE = "#1F2D22"    # very dark sage — card / callout fill on dark

# Earth / territory
TERRITORY_EARTH = "#8B6F47"  # warm brown — Mi'kma'ki callout left border
TERRITORY_BG = "#2A2218"     # warm dark — Mi'kma'ki callout background

# Ochre — evidence-tier B + warm accents
OCHRE_WARM = "#C19A4B"

# Evidence tiers
EV_A = "#4A7C59"             # sage — confirmed
EV_B = "#C19A4B"             # ochre — practitioner pattern
EV_C = "#6B8E9E"             # slate blue — inference
EV_D = "#8C8C8C"             # gray — speculative

# Text + chrome
TEXT_PRIMARY = "#ECECEC"
TEXT_SECONDARY = "#B8B8B8"
TEXT_MUTED = "#7A8C7E"
BG_PRIMARY = "#0E1411"
BG_CARD = "#1A2418"
BORDER_SUBTLE = "#2A3D2E"


def render_styles():
    """Inject global CSS — palette, typography, components."""
    st.markdown(
        f"""
        <style>
        /* ---- Typography: load Source Serif Pro for display headers ---- */
        @import url('https://fonts.googleapis.com/css2?family=Source+Serif+Pro:wght@400;600;700&display=swap');

        /* ---- Slide title (display serif, polished business look) ---- */
        .slide-title {{
            font-family: 'Source Serif Pro', Georgia, serif;
            font-size: 2.6rem;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            margin-bottom: 0.3rem;
            letter-spacing: -0.015em;
            line-height: 1.15;
        }}

        .slide-subtitle {{
            font-family: 'Source Serif Pro', Georgia, serif;
            font-size: 1.25rem;
            color: {TEXT_SECONDARY};
            font-weight: 400;
            font-style: italic;
            margin-bottom: 1.8rem;
            border-bottom: 2px solid {ACCENT};
            padding-bottom: 0.7rem;
        }}

        /* ---- Body markdown ---- */
        .main h1 {{
            font-family: 'Source Serif Pro', Georgia, serif !important;
            color: {TEXT_PRIMARY} !important;
            font-size: 2rem !important;
        }}
        .main h2 {{
            font-family: 'Source Serif Pro', Georgia, serif !important;
            color: {TEXT_PRIMARY} !important;
            font-size: 1.45rem !important;
            margin-top: 1.5rem !important;
        }}
        .main h3 {{
            color: {ACCENT_BRIGHT} !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 1.2rem !important;
        }}
        .main p, .main li {{
            color: {TEXT_SECONDARY} !important;
            line-height: 1.65;
        }}
        .main strong {{
            color: {TEXT_PRIMARY} !important;
        }}
        .main blockquote {{
            border-left: 3px solid {ACCENT};
            padding: 0.5rem 1rem;
            color: {TEXT_MUTED} !important;
            font-style: italic;
            background: {ACCENT_SUBTLE};
            border-radius: 0 4px 4px 0;
        }}
        .main table {{
            width: 100%;
            border-collapse: collapse;
        }}
        .main th {{
            color: {TEXT_PRIMARY} !important;
            background: {ACCENT_SUBTLE} !important;
            font-weight: 600;
            border-bottom: 2px solid {ACCENT} !important;
        }}
        .main td {{
            color: {TEXT_SECONDARY} !important;
            border-bottom: 1px solid {BORDER_SUBTLE} !important;
        }}
        .main hr {{
            border-color: {BORDER_SUBTLE} !important;
            border-top-width: 1px;
        }}
        .main code {{
            color: {ACCENT_BRIGHT} !important;
            background: {ACCENT_SUBTLE} !important;
            padding: 0.1em 0.35em;
            border-radius: 3px;
            font-size: 0.9em;
        }}

        /* ---- Evidence-tier inline badges ---- */
        .ev-badge {{
            display: inline-block;
            font-family: 'Source Serif Pro', Georgia, serif;
            font-weight: 700;
            font-size: 0.78rem;
            padding: 0.12em 0.55em;
            border-radius: 3px;
            margin: 0 0.15em;
            vertical-align: 0.05em;
            letter-spacing: 0.04em;
        }}
        .ev-A {{ background: {EV_A}; color: #fff; }}
        .ev-B {{ background: {EV_B}; color: #1a1a1a; }}
        .ev-C {{ background: transparent; color: {EV_C}; border: 1px solid {EV_C}; }}
        .ev-D {{ background: transparent; color: {EV_D}; border: 1px solid {EV_D}; }}

        /* ---- v1.0.4-candidate update marker ---- */
        .update-badge {{
            display: inline-block;
            font-size: 0.7rem;
            font-weight: 600;
            padding: 0.18em 0.55em;
            border-radius: 3px;
            background: {OCHRE_WARM};
            color: #1a1a1a;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin-left: 0.5em;
            vertical-align: 0.15em;
        }}

        /* ---- Routing arrow accent (hybrid framing visual cue) ---- */
        .arrow-accent {{
            color: {ACCENT};
            font-weight: 700;
            margin: 0 0.3em;
        }}

        /* ---- Mi'kma'ki territory callout ---- */
        .territory-callout {{
            background: {TERRITORY_BG};
            border-left: 4px solid {TERRITORY_EARTH};
            padding: 1.1rem 1.4rem;
            margin: 1.5rem 0;
            border-radius: 0 4px 4px 0;
        }}
        .territory-callout .territory-label {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: {TERRITORY_EARTH};
            margin-bottom: 0.5rem;
        }}
        .territory-callout p {{
            color: {TEXT_PRIMARY} !important;
            font-style: italic;
            line-height: 1.55;
            margin: 0;
        }}

        /* ---- Decision-support callout (suggests-language sections) ---- */
        .decision-callout {{
            background: {ACCENT_SUBTLE};
            border-left: 4px solid {ACCENT};
            padding: 0.9rem 1.2rem;
            margin: 1rem 0;
            border-radius: 0 4px 4px 0;
        }}
        .decision-callout .decision-label {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: {ACCENT_BRIGHT};
            margin-bottom: 0.4rem;
        }}
        .decision-callout p {{
            color: {TEXT_PRIMARY} !important;
            margin: 0;
        }}

        /* ---- Routing callout (routes-language sections) ---- */
        .routing-callout {{
            background: {BG_CARD};
            border-left: 4px solid {OCHRE_WARM};
            padding: 0.9rem 1.2rem;
            margin: 1rem 0;
            border-radius: 0 4px 4px 0;
        }}
        .routing-callout .routing-label {{
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: {OCHRE_WARM};
            margin-bottom: 0.4rem;
        }}
        .routing-callout p {{
            color: {TEXT_PRIMARY} !important;
            margin: 0;
        }}

        /* ---- Section divider with label ---- */
        .section-divider {{
            display: flex;
            align-items: center;
            text-align: center;
            margin: 2rem 0 1.2rem 0;
        }}
        .section-divider::before, .section-divider::after {{
            content: '';
            flex: 1;
            border-bottom: 1px solid {BORDER_SUBTLE};
        }}
        .section-divider span {{
            padding: 0 1rem;
            color: {ACCENT_BRIGHT};
            font-size: 0.78rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.12em;
        }}

        /* ---- NS quantitative anchor stat block ---- */
        .stat-block {{
            display: inline-block;
            margin: 0.5rem 1.5rem 0.5rem 0;
            padding: 0.4rem 0.9rem;
            background: {ACCENT_SUBTLE};
            border-radius: 4px;
            border-left: 3px solid {ACCENT};
        }}
        .stat-block .stat-num {{
            font-family: 'Source Serif Pro', Georgia, serif;
            font-size: 1.4rem;
            font-weight: 700;
            color: {TEXT_PRIMARY};
            display: block;
            line-height: 1;
        }}
        .stat-block .stat-label {{
            font-size: 0.72rem;
            color: {TEXT_MUTED};
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-top: 0.2rem;
            display: block;
        }}

        /* ---- Slide counter ---- */
        .slide-counter {{
            font-size: 0.8rem;
            color: {TEXT_MUTED};
            margin-bottom: 0.5rem;
        }}

        /* ---- Sidebar group color coding ---- */
        section[data-testid="stSidebar"] {{
            background: {BG_PRIMARY};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_slide_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="slide-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="slide-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_slide_body(body: str):
    """Render slide body markdown WITH HTML allowed.

    v1.0.4 change: previously unsafe_allow_html=False; now True so that slide
    markdown can include territory callouts, evidence-tier badges, section
    dividers, and other in-content components. Slide files are author-controlled
    (not user input) so HTML injection is safe in this context.
    """
    st.markdown(body, unsafe_allow_html=True)


def render_nav_controls(current_idx: int, total: int):
    """Render previous/next navigation. Returns (go_prev, go_next) booleans."""
    col_prev, col_counter, col_next = st.columns([1, 2, 1])
    go_prev = False
    go_next = False
    with col_prev:
        if current_idx > 0:
            go_prev = st.button("Previous", use_container_width=True)
    with col_counter:
        st.markdown(
            f'<div style="text-align:center; color:{TEXT_MUTED}; padding-top:0.4rem;">'
            f'{current_idx + 1} / {total}</div>',
            unsafe_allow_html=True,
        )
    with col_next:
        if current_idx < total - 1:
            go_next = st.button("Next", use_container_width=True)
    return go_prev, go_next


def render_landscape_pdf_download(pdf_path: str, filename: str = "Klara_Landscape_v1_0_3.pdf"):
    """Render a prominent download button for the v1.0.3 landscape PDF.

    Used on slide 11 (Where the Landscape Stands). PDF lives at
    presentation/assets/landscape/ in the repo so it ships with the deck.
    """
    from pathlib import Path
    p = Path(pdf_path)
    if not p.exists():
        st.warning(f"Landscape PDF not yet bundled with deck (expected at {pdf_path}). "
                   "Add it via the build/deploy process before relying on this button.")
        return
    with open(p, "rb") as f:
        st.download_button(
            label=f"Download {filename}  (~{p.stat().st_size // 1024} KB)",
            data=f.read(),
            file_name=filename,
            mime="application/pdf",
            type="primary",
            use_container_width=False,
        )
