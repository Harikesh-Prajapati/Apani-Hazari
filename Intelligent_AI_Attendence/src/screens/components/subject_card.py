import streamlit as st
from html import escape


def subject_card(
    name,
    code,
    section,
    stats=None,
    footer_callback=None,
):
    # Card styling
    st.markdown(
        """
        <style>
        .subject-card {
            background: #ffffff;
            border: 1px solid #a3a3a3;
            border-radius: 22px;
            padding: 24px 28px;
            margin: 12px 0 16px 0;
            color: #111827;
        }

        .subject-title {
            color: #111827;
            font-size: 25px;
            font-weight: 700;
            margin-bottom: 22px;
        }

        .subject-details {
            color: #6b7280;
            font-size: 17px;
            margin-bottom: 18px;
        }

        .subject-code {
            display: inline-block;
            background: #eeeeff;
            color: #6366f1;
            border-radius: 7px;
            padding: 4px 10px;
        }

        .subject-section {
            color: #374151;
            font-weight: 600;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Open the card and render its title and details.
    st.markdown(
        f"""
        <div class="subject-card">
            <div class="subject-title">{escape(str(name))}</div>
            <div class="subject-details">
                Code:
                <span class="subject-code">{escape(str(code))}</span>
                <span style="color:#d1d5db;"> | </span>
                Section:
                <span class="subject-section">{escape(str(section))}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Native Streamlit badges: no badge HTML to accidentally show as code.
    stats = stats or []

    if stats:
        badge_columns = st.columns(len(stats))

        for column, stat in zip(badge_columns, stats):
            icon, label, value = stat

            with column:
                st.markdown(
                    f"""
                    <div style="
                        background:#fff1f6;
                        color:#111827;
                        border-radius:12px;
                        padding:9px 12px;
                        margin-bottom:8px;
                        text-align:center;
                    ">
                        {escape(str(icon))}
                        <b>{escape(str(value))}</b>
                        {escape(str(label))}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    if footer_callback:
        footer_callback()



