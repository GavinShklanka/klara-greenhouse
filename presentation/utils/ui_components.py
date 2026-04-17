"""
UI components - reusable Streamlit rendering functions for the presentation surface.
Dark theme, high contrast, greenhouse green accent.
"""

import streamlit as st


ACCENT = "#22c55e"
ACCENT_DIM = "#166534"
ACCENT_SUBTLE = "#1a2e1e"
BORDER_COLOR = "#2a3d2e"
TEXT_BODY = "#c8c8c8"


def render_styles():
    """Inject global CSS into the Streamlit page."""
    st.markdown(
        f"""
        <style>
        /* Slide title - near-white, large, strong */
        .slide-title {{
            font-size: 2.4rem;
            font-weight: 700;
            color: #f0f0f0;
            margin-bottom: 0.2rem;
            letter-spacing: -0.02em;
            line-height: 1.2;
        }}

        /* Slide subtitle - lighter gray, ruled underline */
        .slide-subtitle {{
            font-size: 1.15rem;
            color: #d4d4d4;
            font-weight: 400;
            margin-bottom: 2rem;
            border-bottom: 2px solid {ACCENT};
            padding-bottom: 0.65rem;
        }}

        /* Body markdown gets Streamlit defaults (textColor from theme) */

        /* Override Streamlit's default h1/h2/h3 inside main content */
        .main h1 {{
            color: #f0f0f0 !important;
            font-size: 2rem !important;
        }}
        .main h2 {{
            color: #d4d4d4 !important;
            font-size: 1.4rem !important;
        }}
        .main h3 {{
            color: #c8d8cc !important;
            font-size: 1.15rem !important;
        }}
        .main p, .main li {{
            color: #c8c8c8 !important;
        }}
        .main strong {{
            color: #e8e8e8 !important;
        }}
        .main blockquote {{
            border-left: 3px solid {ACCENT};
            padding-left: 1rem;
            color: #a0b8a4 !important;
        }}
        .main table {{
            width: 100%;
        }}
        .main th {{
            color: #e0e0e0 !important;
            background: {ACCENT_SUBTLE} !important;
            font-weight: 600;
        }}
        .main td {{
            color: #c8c8c8 !important;
        }}
        .main hr {{
            border-color: {BORDER_COLOR} !important;
        }}
        .main code {{
            color: {ACCENT} !important;
        }}

        /* Nav counter */
        .slide-counter {{
            font-size: 0.8rem;
            color: #6b8c70;
            margin-bottom: 0.5rem;
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
    st.markdown(body, unsafe_allow_html=False)


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
            f'<div style="text-align:center; color:#6b8c70; padding-top:0.4rem;">'
            f'{current_idx + 1} / {total}</div>',
            unsafe_allow_html=True,
        )
    with col_next:
        if current_idx < total - 1:
            go_next = st.button("Next", use_container_width=True)
    return go_prev, go_next
