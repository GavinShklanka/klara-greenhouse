"""
UI components — reusable Streamlit rendering functions for the presentation surface.
"""

import streamlit as st


ACCENT = "#4A7C59"
ACCENT_LIGHT = "#E8F0EB"
WARNING_COLOR = "#C0392B"
NOTE_BG = "#F7F9F8"
BORDER_COLOR = "#D9E3DB"


def render_styles():
    """Inject global CSS into the Streamlit page."""
    st.markdown(
        f"""
        <style>
        /* Typography */
        .slide-title {{
            font-size: 2.4rem;
            font-weight: 700;
            color: #1A1A1A;
            margin-bottom: 0.25rem;
            letter-spacing: -0.02em;
            line-height: 1.2;
        }}
        .slide-subtitle {{
            font-size: 1.2rem;
            color: #555;
            font-weight: 400;
            margin-bottom: 2rem;
            border-bottom: 2px solid {ACCENT};
            padding-bottom: 0.75rem;
        }}
        .slide-body {{
            font-size: 1.05rem;
            line-height: 1.75;
            color: #2C2C2C;
        }}

        /* Callout boxes */
        .scope-flag-box {{
            background: #FDF3F2;
            border-left: 4px solid {WARNING_COLOR};
            padding: 0.75rem 1rem;
            border-radius: 4px;
            margin: 1rem 0;
            font-size: 0.9rem;
        }}
        .speaker-notes-box {{
            background: {NOTE_BG};
            border: 1px solid {BORDER_COLOR};
            border-left: 4px solid {ACCENT};
            padding: 1rem 1.25rem;
            border-radius: 4px;
            margin-top: 1.5rem;
        }}
        .do-not-say-box {{
            background: #FDF8F2;
            border: 1px solid #E8D9C5;
            border-left: 4px solid #C07D39;
            padding: 1rem 1.25rem;
            border-radius: 4px;
            margin-top: 1rem;
        }}
        .impl-notes-box {{
            background: #F2F4FD;
            border: 1px solid #C5CCE8;
            border-left: 4px solid #3949AB;
            padding: 1rem 1.25rem;
            border-radius: 4px;
            margin-top: 1rem;
        }}
        .scope-boundary-box {{
            background: {ACCENT_LIGHT};
            border: 1px solid {ACCENT};
            padding: 0.75rem 1rem;
            border-radius: 4px;
            margin: 1.5rem 0;
            font-size: 0.95rem;
            font-weight: 600;
            color: #1A3D26;
        }}
        .now-next-later {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 1rem;
            margin: 1.5rem 0;
        }}
        .now-next-later-card {{
            padding: 1rem;
            border-radius: 6px;
            border: 1px solid {BORDER_COLOR};
        }}
        .now-card {{ border-top: 3px solid {ACCENT}; background: {ACCENT_LIGHT}; }}
        .next-card {{ border-top: 3px solid #7BA7BC; background: #EFF4F7; }}
        .later-card {{ border-top: 3px solid #AAA; background: #F5F5F5; }}

        /* Sidebar */
        .slide-counter {{
            font-size: 0.8rem;
            color: #888;
            margin-bottom: 0.5rem;
        }}

        /* Mode badge */
        .mode-badge {{
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}
        .mode-presentation {{ background: {ACCENT_LIGHT}; color: #1A3D26; }}
        .mode-working {{ background: #EBF0FD; color: #1A2A6B; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_slide_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="slide-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="slide-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_scope_flags(flags: list[str]):
    if not flags:
        return
    phrases = ", ".join(f'<code>{f}</code>' for f in flags)
    st.markdown(
        f'<div class="scope-flag-box">⚠️ <strong>Scope drift detected:</strong> {phrases}</div>',
        unsafe_allow_html=True,
    )


def render_speaker_notes(notes: str):
    if not notes:
        return
    st.markdown(
        f'<div class="speaker-notes-box"><strong>Speaker Notes</strong><br><br>{_md_to_inline(notes)}</div>',
        unsafe_allow_html=True,
    )


def render_do_not_say(notes: str):
    if not notes:
        return
    st.markdown(
        f'<div class="do-not-say-box"><strong>Do Not Say</strong><br><br>{_md_to_inline(notes)}</div>',
        unsafe_allow_html=True,
    )


def render_implementation_notes(notes: str):
    if not notes:
        return
    st.markdown(
        f'<div class="impl-notes-box"><strong>Implementation Notes</strong><br><br>{_md_to_inline(notes)}</div>',
        unsafe_allow_html=True,
    )


def render_scope_boundary():
    st.markdown(
        f'<div class="scope-boundary-box">Layer 1 scope boundary — content below this line is roadmap only, not current scope.</div>',
        unsafe_allow_html=True,
    )


def render_slide_body(body: str):
    st.markdown(body, unsafe_allow_html=False)


def render_nav_controls(current_idx: int, total: int):
    """Render previous/next navigation. Returns (go_prev, go_next) booleans."""
    col_prev, col_counter, col_next = st.columns([1, 2, 1])
    go_prev = False
    go_next = False
    with col_prev:
        if current_idx > 0:
            go_prev = st.button("← Previous", use_container_width=True)
    with col_counter:
        st.markdown(
            f'<div style="text-align:center; color:#888; padding-top:0.4rem;">'
            f'{current_idx + 1} / {total}</div>',
            unsafe_allow_html=True,
        )
    with col_next:
        if current_idx < total - 1:
            go_next = st.button("Next →", use_container_width=True)
    return go_prev, go_next


def render_mode_badge(mode: str):
    css_class = "mode-presentation" if mode == "presentation" else "mode-working"
    label = "Presentation" if mode == "presentation" else "Working"
    st.markdown(
        f'<span class="mode-badge {css_class}">{label} Mode</span>',
        unsafe_allow_html=True,
    )


def _md_to_inline(text: str) -> str:
    """Very light markdown → HTML for use inside HTML blocks (headings stripped to bold)."""
    import re
    # Strip ## heading markers, make them bold instead
    text = re.sub(r"^#{1,3}\s+(.+)$", r"<strong>\1</strong>", text, flags=re.MULTILINE)
    # Preserve line breaks
    text = text.replace("\n\n", "<br><br>").replace("\n", "<br>")
    return text
