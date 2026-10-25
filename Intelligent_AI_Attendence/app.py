import importlib
import importlib.util
import traceback
import sys
import glob
from importlib import metadata

import streamlit as st

st.set_page_config(
    page_title="Apani Hazari - Making Attendance Faster Using AI",
    page_icon="🎓",
)

# Diagnose Supabase before importing application screens.
st.subheader("Supabase Dependency Diagnostic")
st.write("Python:", sys.executable, sys.version)

try:
    st.write("Supabase version:", metadata.version("supabase"))
except Exception as e:
    st.write("Supabase metadata:", repr(e))

try:
    st.write("Supabase module:", importlib.util.find_spec("supabase"))
except Exception as e:
    st.write("Module lookup error:", repr(e))

st.write(
    "Supabase files:",
    glob.glob(f"{sys.prefix}/lib/python*/site-packages/supabase*"),
)

try:
    from supabase import create_client, Client
    st.success("Supabase import successful!")
except Exception:
    st.error("Supabase import failed:")
    st.code(traceback.format_exc())
    st.stop()

# Load application screens only after Supabase is verified.
try:
    importlib.invalidate_caches()
    from src.screens.home_screen import home_screen
    from src.screens.student_screen import student_screen
    from src.screens.teacher_screen import teacher_screen
    from src.screens.components.dialog_auto_enroll import auto_enroll_dialog
except Exception:
    st.error("Application screen import failed:")
    st.code(traceback.format_exc())
    st.stop()









