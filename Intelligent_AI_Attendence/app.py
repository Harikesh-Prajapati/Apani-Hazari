import traceback

import streamlit as st

# Must be the first Streamlit command, so it runs before the app's own imports.
st.set_page_config(
    page_title="Apani Hazari - Making Attendance Faster Using AI",
    page_icon="https://cdn-icons-png.magnific.com/256/18492/18492086.png",
)

# Show the real error on the page if an import fails (Streamlit Cloud hides it).
try:
    from src.screens.home_screen import home_screen
    from src.screens.student_screen import student_screen
    from src.screens.teacher_screen import teacher_screen
    from src.screens.components.dialog_auto_enroll import auto_enroll_dialog
except Exception:
    st.error("The app failed to start. Details:")
    st.code(traceback.format_exc())
    st.stop()


def main():
    # Initialize session state.
    if "login_type" not in st.session_state:
        st.session_state["login_type"] = None

    # Read a student invitation code from the URL, then remove it from the URL
    # so the dialog doesn't reopen on every rerun.
    join_code = st.query_params.get("join-code")

    if join_code:
        st.session_state["pending_join_code"] = join_code
        del st.query_params["join-code"]

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










