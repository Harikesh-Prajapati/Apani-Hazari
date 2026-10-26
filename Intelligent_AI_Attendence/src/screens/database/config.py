import importlib
import subprocess
import sys
from importlib import metadata
from pathlib import Path

import streamlit as st


def _pip_install(package):
    return subprocess.run(
        [sys.executable, "-m", "pip", "install", package],
        capture_output=True,
        text=True,
    )


def _load_supabase():
    """Import supabase. If it's missing, try to install it once, and show why if that fails."""
    try:
        from supabase import create_client
        return create_client
    except ModuleNotFoundError as first_error:
        st.warning("supabase is missing from this environment. Trying to install it now...")

        result = _pip_install("supabase")
        if result.returncode != 0:
            # pip itself may be missing: bootstrap it and retry
            subprocess.run(
                [sys.executable, "-m", "ensurepip", "--upgrade"],
                capture_output=True,
                text=True,
            )
            result = _pip_install("supabase")

        importlib.invalidate_caches()

        try:
            from supabase import create_client
            st.success("supabase was installed. Reload the page if anything looks off.")
            return create_client
        except Exception as e:
            st.error(f"Could not import supabase: {type(e).__name__}: {e}")
            st.write("Original error:", repr(first_error))
            st.write("pip exit code:", result.returncode)
            st.code((result.stdout or "")[-2500:] + "\n" + (result.stderr or "")[-2500:], language="text")

            here = Path(__file__).resolve()
            for p in here.parents:
                f = p / "requirements.txt"
                if f.exists():
                    raw = f.read_bytes()
                    st.write("requirements file:", str(f), "| first bytes:", raw[:12])
                    st.code(raw.decode("utf-8", errors="replace"), language="text")
                    break

            names = sorted({(d.metadata["Name"] or "").lower() for d in metadata.distributions()})
            st.write(f"{len(names)} packages installed:", names)
            st.stop()


create_client = _load_supabase()

try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"].strip().rstrip("/")
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"].strip()
except KeyError as e:
    st.error(f"Missing secret: {e}. Add it in Manage app -> Settings -> Secrets.")
    st.stop()

if SUPABASE_URL.endswith("/rest/v1"):
    SUPABASE_URL = SUPABASE_URL.removesuffix("/rest/v1")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

