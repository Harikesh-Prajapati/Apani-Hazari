import streamlit as st

from src.screens.database.db import create_attendance


def show_attendance_result(df, logs):
    """Display attendance results for review inside an existing dialog."""

    st.write("Please review attendance before confirming.")
    st.dataframe(df, hide_index=True, width="stretch")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Discard",
            width="stretch",
            key="discard_attendance_results",
        ):
            st.session_state["voice_attendance_results"] = None
            st.rerun()

    with col2:
        if st.button(
            "Confirm & Save",
            width="stretch",
            type="primary",
            key="confirm_attendance_results",
        ):
            try:
                create_attendance(logs)
                st.toast("Attendance saved successfully!")
                st.session_state["voice_attendance_results"] = None
                st.rerun()

            except Exception as e:
                st.error(f"Failed to save attendance: {e}")


@st.dialog("Attendance Reports")
def attendance_result_dialog(df, logs):
    """Open attendance results in a separate dialog."""

    show_attendance_result(df, logs)














