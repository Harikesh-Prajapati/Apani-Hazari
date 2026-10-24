
import streamlit as st
from supabase import create_client, Client

supabase: Client = create_client(
    st.secrets["SUPABASE_URL"].strip().rstrip("/"),
    st.secrets["SUPABASE_KEY"].strip()
)

