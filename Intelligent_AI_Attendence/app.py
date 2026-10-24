
import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.student_screen import student_screen
from src.screens.teacher_screen import teacher_screen
from src.screens.components.dialog_auto_enroll import auto_enroll_dialog


def main():
    # Must be the first Streamlit command in the app.
    st.set_page_config(
        page_title="Apani Hazari - Making Attendance Faster Using AI",
        page_icon="https://cdn-icons-png.magnific.com/256/18492/18492086.png",
    )

    # Initialize session state.
    if "login_type" not in st.session_state:
        st.session_state["login_type"] = None

    # Read a student invitation code from the URL.
    join_code = st.query_params.get("join-code")

    if join_code:
        st.session_state["pending_join_code"] = join_code

        # Route to student login if necessary.
        if st.session_state.get("login_type") != "student":
            st.session_state["login_type"] = "student"
            st.rerun()

    # Route to the appropriate screen.
    login_type = st.session_state.get("login_type")

    if login_type == "teacher":
        teacher_screen()

    elif login_type == "student":
        student_screen()

    else:
        home_screen()

    # Enroll the student after successful login.
    pending_code = st.session_state.get("pending_join_code")

    if (
        pending_code
        and st.session_state.get("is_logged_in")
        and st.session_state.get("user_role") == "student"
    ):
        auto_enroll_dialog(pending_code)


if __name__ == "__main__":
    main()










