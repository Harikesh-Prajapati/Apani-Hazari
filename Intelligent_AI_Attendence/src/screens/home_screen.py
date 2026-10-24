import streamlit as st
 
from src.screens.components.header import header_home
from src.screens.components.footer import footer_home
from src.screens.ui.base_layout import (
    style_base_layout,
    style_background_home,
)
 
STUDENT_IMAGE = "https://i.ibb.co/844D9Lrt/mascot-student.png"
TEACHER_IMAGE = "https://i.ibb.co/CsmQQV6X/mascot-prof.png"
 
 
def home_screen():
    """Home screen for the Apani Hazari attendance application."""
 
    header_home()
    style_background_home()
    style_base_layout()
 
    # -------------------- CUSTOM STYLING --------------------
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
 
        html, body, [class*="css"],
        [data-testid="stAppViewContainer"],
        [data-testid="stMarkdownContainer"],
        button, input {
            font-family: 'Inter', sans-serif !important;
        }
 
        [data-testid="stAppViewContainer"] {
            background: #5865F2;
        }
 
        .block-container {
            max-width: 1120px;
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
        }
 
        header[data-testid="stHeader"] {
            background: transparent;
        }
 
        /* Force Inter on the "Apani Hazari" title (and all text) from header_home(),
           even if it uses inline styles or its own font-family */
        [data-testid="stMarkdownContainer"] *,
        [data-testid="stHtml"] *,
        .stMarkdown *,
        h1, h2, h3, h1 *, h2 *, h3 * {
            font-family: 'Inter', sans-serif !important;
        }
 
        /* Tight line spacing for the title block (first block on the page) */
        [data-testid="stVerticalBlock"] > div:first-child [data-testid="stMarkdownContainer"] *,
        [data-testid="stVerticalBlock"] > div:first-child [data-testid="stHtml"] * {
            line-height: 1.0 !important;
        }
 
        /* Override the title drawn by header_home(): Inter + tight line spacing */
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h1 *,
        [data-testid="stMarkdownContainer"] h2 * {
            font-family: 'Inter', sans-serif !important;
            font-weight: 800 !important;
            letter-spacing: -1.5px !important;
            line-height: 1.0 !important;
            margin-top: 0 !important;
            margin-bottom: 0.4rem !important;
            padding: 0 !important;
        }
 
        h1.brand-title,
        .brand-title {
            font-family: 'Inter', sans-serif !important;
            font-size: clamp(2rem, 3.2vw, 2.7rem) !important;
            font-weight: 800 !important;
            letter-spacing: -1.5px !important;
            line-height: 1.0 !important;
            text-align: center;
            color: #E0E3FF;
            margin: 0 0 0.8rem 0 !important;
            padding: 0 !important;
        }
 
        .brand-label {
            display: table;
            position: relative;
            top: -1.2rem;              /* moves the label up, closer to the title */
            margin: 0 auto 0.6rem auto;
            padding: 8px 16px;
            border-radius: 30px;
            background: #FFE7F3;
            color: #D91B87;
            font-family: 'Inter', sans-serif !important;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.4px;
            text-align: center;
        }
 
        /* Matching portal cards */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #E0E3FF;
            border: 1px solid rgba(255, 255, 255, 0.35);
            border-radius: 24px;
            padding: 22px 26px;
            box-sizing: border-box;
        }
 
        .portal-eyebrow {
            text-align: center;
            color: #D91B87;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.4px;
            margin: 0 0 10px 0;
        }
 
        .portal-title {
            text-align: center;
            color: #171A35;
            font-size: 25px;
            font-weight: 800;
            letter-spacing: -0.8px;
            line-height: 1.2;
            margin: 0 0 10px 0;
        }
 
        .portal-description {
            color: #626B8A;
            text-align: center;
            font-size: 13px;
            line-height: 1.55;
            min-height: 42px;
            margin: 0 0 12px 0;
        }
 
        /* Equal mascot area for both portals */
        .mascot-slot {
            width: 100%;
            height: 175px;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            margin: 0 0 14px 0;
        }
 
        .mascot-slot img {
            display: block;
            width: 100%;
            height: 175px;
            object-fit: contain;
            object-position: center;
        }
 
        /* Same button dimensions and styling */
        div.stButton > button {
            width: 100%;
            min-height: 50px;
            background: #EB459E;
            color: #FFFFFF;
            border: 1px solid transparent;
            border-radius: 14px;
            font-family: 'Inter', sans-serif !important;
            font-size: 14px;
            font-weight: 700;
            transition: background 0.2s ease, transform 0.2s ease;
        }
 
        div.stButton > button:hover {
            background: #D9368D;
            color: #FFFFFF;
            border-color: transparent;
            transform: translateY(-1px);
        }
 
        div.stButton > button:focus {
            color: #FFFFFF;
        }
 
        /* Mobile layout */
        @media (max-width: 700px) {
            .block-container {
                padding: 1rem 0.8rem;
            }
 
            h1.brand-title,
            .brand-title {
                font-size: clamp(1.7rem, 7vw, 2.2rem) !important;
                letter-spacing: -1px !important;
            }
 
            .brand-label {
                top: -0.8rem;
                margin-bottom: 0.4rem;
                font-size: 10px;
            }
 
            div[data-testid="stVerticalBlockBorderWrapper"] {
                padding: 16px 12px;
                border-radius: 18px;
            }
 
            .portal-title {
                font-size: 20px;
            }
 
            .portal-description {
                font-size: 12px;
                min-height: 58px;
            }
 
            .mascot-slot,
            .mascot-slot img {
                height: 130px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
 
    # -------------------- BRAND TITLE + LABEL --------------------
    st.markdown(
        '<div class="brand-label">✦ SMART ATTENDANCE PLATFORM</div>',
        unsafe_allow_html=True,
    )
 
    # -------------------- PORTAL CARDS --------------------
    student_col, teacher_col = st.columns(2, gap="large")
 
    # Student Portal
    with student_col:
        with st.container(border=True):
            st.markdown(
                """
                <div class="portal-eyebrow">LEARNER ACCESS</div>
                <div class="portal-title">Student Portal</div>
                <div class="portal-description">
                    View your classes, check attendance, and stay up to date.
                </div>
                """,
                unsafe_allow_html=True,
            )
 
            st.markdown(
                f"""
                <div class="mascot-slot">
                    <img src="{STUDENT_IMAGE}" alt="Student mascot">
                </div>
                """,
                unsafe_allow_html=True,
            )
 
            if st.button(
                "I'm a Student ↗",
                key="home_student_button",
                use_container_width=True,
            ):
                st.session_state["login_type"] = "student"
                st.rerun()
 
    # Teacher Portal
    with teacher_col:
        with st.container(border=True):
            st.markdown(
                """
                <div class="portal-eyebrow">EDUCATOR ACCESS</div>
                <div class="portal-title">Teacher Portal</div>
                <div class="portal-description">
                    Manage classes, record attendance, and review student records.
                </div>
                """,
                unsafe_allow_html=True,
            )
 
            st.markdown(
                f"""
                <div class="mascot-slot">
                    <img src="{TEACHER_IMAGE}" alt="Teacher mascot">
                </div>
                """,
                unsafe_allow_html=True,
            )
 
            if st.button(
                "I'm a Teacher ↗",
                key="home_teacher_button",
                use_container_width=True,
            ):
                st.session_state["login_type"] = "teacher"
                st.rerun()
 
    # -------------------- FOOTER --------------------
    footer_home()
 






