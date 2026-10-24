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






























