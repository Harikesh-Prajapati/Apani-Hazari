from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from PIPELINE.voice_pipeline import process_bulk_audio
from src.screens.database.config import supabase
from src.screens.components.dialog_attendance_results import (
    show_attendance_result,
)



VOICE_THRESHOLD = 0.60


@st.dialog("Voice Attendance")
def voice_attendance_dialog(selected_subject_id):
    st.write(
        "Record students saying 'I am present, my name is ...' "
        "one at a time, with a 1 second pause between students."
    )

    st.session_state.setdefault("voice_attendance_results", None)

    audio_data = st.audio_input("Record classroom audio")

    if st.button(
        "Analyze Audio",
        width="stretch",
        type="primary",
        key="analyze_voice_audio",
    ):
        if audio_data is None:
            st.warning("Please record audio before analyzing.")
            return

        with st.spinner("Processing audio data..."):
            try:
                enrolled_res = (
                    supabase.table("subject_students")
                    .select("*, students(*)")
                    .eq("subject_id", selected_subject_id)
                    .execute()
                )

                enrolled_students = enrolled_res.data or []

                if not enrolled_students:
                    st.warning("No students are enrolled in this subject.")
                    return

                candidates_dict = {
                    node["students"]["student_id"]:
                    node["students"]["voice_embedding"]
                    for node in enrolled_students
                    if node.get("students")
                    and node["students"].get("voice_embedding")
                }

                if not candidates_dict:
                    st.error(
                        "No enrolled students have registered voice profiles."
                    )
                    return

                detected_scores, best_raw = process_bulk_audio(
                    audio_data.getvalue(),
                    candidates_dict,
                    threshold=VOICE_THRESHOLD,
                    return_debug=True,
                )

                results = []
                attendance_to_log = []

                current_timestamp = datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S+00:00"
                )

                for node in enrolled_students:
                    student = node.get("students")

                    if not student:
                        continue

                    student_id = student["student_id"]
                    is_present = student_id in detected_scores

                    if student_id not in candidates_dict:
                        score_text = "no voice profile"
                    elif student_id in best_raw:
                        score_text = f"{best_raw[student_id]:.2f}"
                    else:
                        score_text = "-"

                    results.append({
                        "Name": student.get("name", "Unknown"),
                        "ID": student_id,
                        "Score": score_text,
                        "Status": "Present" if is_present else "Absent",
                    })

                    attendance_to_log.append({
                        "student_id": student_id,
                        "subject_id": selected_subject_id,
                        "timestamp": current_timestamp,
                        "is_present": is_present,
                    })

                st.session_state["voice_attendance_results"] = (
                    pd.DataFrame(results),
                    attendance_to_log,
                )

                
                st.rerun(scope="fragment")

            except Exception as e:
                st.error(f"Audio analysis failed: {e}")

   
    saved_results = st.session_state.get("voice_attendance_results")

    if saved_results:
        st.divider()
        df_results, logs = saved_results
        show_attendance_result(df_results, logs)





































