import streamlit as st

# If the package is missing, show the real reason on the page
# (Streamlit Cloud hides the normal error message).
try:
    from supabase import create_client, Client
except Exception as e:
    st.error(f"Could not import supabase: {type(e).__name__}: {e}")
    st.stop()

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"].strip().rstrip("/")
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"].strip()
except KeyError as e:
    st.error(f"Missing secret: {e}. Add it in Manage app -> Settings -> Secrets.")
    st.stop()

if SUPABASE_URL.endswith("/rest/v1"):
    SUPABASE_URL = SUPABASE_URL.removesuffix("/rest/v1")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


