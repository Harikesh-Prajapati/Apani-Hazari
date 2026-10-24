import io
from urllib.parse import quote

import segno
import streamlit as st


APP_URL = "https://apani-hazari.streamlit.app"


@st.dialog("Share Class Link")
def share_subject_dialog(subject_name, subject_code):
    join_url = f"{APP_URL}/?join-code={quote(str(subject_code))}"

    st.header("Scan to Join")
    st.caption(f"{subject_name} - Code: {subject_code}")

    qr = segno.make(join_url)

    out = io.BytesIO()
    qr.save(out, kind='png', scale=10, border=1)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('### Copy Link')
        st.code(join_url, language="text")
        st.code(subject_code, language="text")
        st.info('Copy this link to share on WhatsApp or Email')

    with col2:
        st.markdown('### QR Code')
        st.image(out.getvalue(), caption='QR code for class joining')






























# @st.dialog("Share Class Link", width="large")
# def share_subject_dialog(subject_name, subject_code):

#     # Change this to your public app URL when deploying.
#     app_domain = "Apani Hazari-main.streamlit.app"

#     query = urlencode({"join-code": str(subject_code)})
#     join_url = f"{app_domain}/?{query}"

#     # Dialog styling
#     st.markdown(
#         """
#         <style>
#         /* White modal background */
#         div[data-testid="stDialog"] > div {
#             background: #ffffff !important;
#             border-radius: 28px !important;
#             color: #17233f !important;
#             padding: 24px !important;
#         }

#         /* Headings and text */
#         div[data-testid="stDialog"] h2,
#         div[data-testid="stDialog"] h3,
#         div[data-testid="stDialog"] h4,
#         div[data-testid="stDialog"] p,
#         div[data-testid="stDialog"] label {
#             color: #17233f !important;
#         }

#         div[data-testid="stDialog"] h2 {
#             font-size: 2rem !important;
#             font-weight: 750 !important;
#         }

#         div[data-testid="stDialog"] h3 {
#             font-size: 1.25rem !important;
#             font-weight: 700 !important;
#         }

#         /* Light code boxes */
#         div[data-testid="stDialog"] pre {
#             background: #f1f4fa !important;
#             border: 1px solid #e4e9f3 !important;
#             border-radius: 14px !important;
#             padding: 18px !important;
#         }

#         div[data-testid="stDialog"] pre code {
#             background: transparent !important;
#             color: #17233f !important;
#             font-size: 1rem !important;
#             white-space: pre-wrap !important;
#             overflow-wrap: anywhere !important;
#         }

#         /* Information box */
#         div[data-testid="stDialog"] div[data-testid="stAlert"] {
#             background: #eaf2ff !important;
#             border-radius: 14px !important;
#         }

#         div[data-testid="stDialog"] div[data-testid="stAlert"] p {
#             color: #2878df !important;
#         }

#         /* Blue open-link button */
#         div[data-testid="stDialog"] a {
#             display: flex !important;
#             align-items: center !important;
#             justify-content: center !important;
#             background: #5365f5 !important;
#             color: #ffffff !important;
#             border-radius: 14px !important;
#             padding: 16px !important;
#             text-decoration: none !important;
#             font-weight: 700 !important;
#             min-height: 54px !important;
#         }

#         /* QR image */
#         div[data-testid="stDialog"] img {
#             border-radius: 12px !important;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )

#     st.subheader("Scan to Join")

#     # Generate QR code
#     qr = segno.make(join_url)
#     output = io.BytesIO()
#     qr.save(output, kind="png", scale=8, border=2)
#     output.seek(0)

#     # Two-column layout
#     col1, col2 = st.columns([1, 1], gap="large")

#     with col1:
#         st.markdown("### Copy Link")
#         st.code(join_url, language="text")
#         st.code(str(subject_code), language="text")

#         st.info("Copy this link to share on WhatsApp or email.")

#         st.link_button(
#             "🔗  Open Class Link",
#             join_url,
#             use_container_width=True,
#         )

#     with col2:
#         st.markdown("### Scan to Join")

#         st.image(
#             output.getvalue(),
#             caption="QR code for class joining",
#             use_container_width=True,
#         )







        