import io
import time
from html import escape
import streamlit as st
import numpy as np
from PIL import Image

from src.screens.ui.base_layout import (
    style_background_dashboard,
    style_base_layout,
)
from src.screens.components.header import header_dashboard
from src.screens.components.footer import footer_dashboard
from src.screens.components.dialog_enroll import enroll_dialog

from PIPELINE.face_pipeline import (
    predict_attendance,
    get_face_embeddings,
    train_classifier,
)
from PIPELINE.voice_pipeline import get_voice_embedding

from src.screens.database.db import (
    get_all_students,
    create_student,
    get_student_subjects,
    get_student_attendance,
    unenroll_student_to_subject,
)


def style_student_screen():
    """Inter font for the title/headings; black headings, camera label and spinner text."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        /* ---------- Inter font: "Apani Hazari" title, headings, labels, spinner ---------- */
        [data-testid="stMarkdownContainer"] *:not([data-testid="stIconMaterial"]),
        [data-testid="stHtml"] *,
        [data-testid="stHeading"],
        [data-testid="stHeading"] *,
        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] *,
        [data-testid="stSpinner"],
        [data-testid="stSpinner"] *,
        h1, h2, h3, h1 *, h2 *, h3 * {
            font-family: 'Inter', sans-serif !important;
        }

        /* "Apani Hazari" title: heavy Inter with tight line spacing */
        [data-testid="stMarkdownContainer"] h1,
        [data-testid="stMarkdownContainer"] h2,
        [data-testid="stMarkdownContainer"] h3,
        [data-testid="stMarkdownContainer"] h1 *,
        [data-testid="stMarkdownContainer"] h2 *,
        [data-testid="stMarkdownContainer"] h3 * {
            font-weight: 800 !important;
            letter-spacing: -1px !important;
            line-height: 1.0 !important;
        }

        /* ---------- Black headings: "Login using FaceID", etc. ---------- */
        [data-testid="stHeading"],
        [data-testid="stHeading"] * {
            color: #000000 !important;
            font-weight: 800 !important;
            letter-spacing: -0.5px !important;
        }

        /* ---------- Black labels: "Position your face in the center", etc. ---------- */
        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] *,
        label,
        label * {
            color: #000000 !important;
            font-weight: 600 !important;
        }

        /* ---------- Black spinner text: "AI is scanning.." ---------- */
        [data-testid="stSpinner"],
        [data-testid="stSpinner"] *,
        [data-testid="stSpinner"] p {
            color: #000000 !important;
            font-weight: 600 !important;
        }

        /* ---------- Dialogs (dark background): keep headings/labels white ---------- */
        [data-testid="stDialog"] [data-testid="stHeading"],
        [data-testid="stDialog"] [data-testid="stHeading"] *,
        [data-testid="stDialog"] [data-testid="stWidgetLabel"],
        [data-testid="stDialog"] [data-testid="stWidgetLabel"] *,
        [data-testid="stDialog"] label,
        [data-testid="stDialog"] label *,
        div[role="dialog"] [data-testid="stHeading"],
        div[role="dialog"] [data-testid="stHeading"] *,
        div[role="dialog"] [data-testid="stWidgetLabel"],
        div[role="dialog"] [data-testid="stWidgetLabel"] *,
        div[role="dialog"] label,
        div[role="dialog"] label *,
        div[role="dialog"] [data-testid="stSpinner"],
        div[role="dialog"] [data-testid="stSpinner"] * {
            color: #FFFFFF !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _sd_css():
    st.markdown(
        """
        <style>
        .sd-cards {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
            margin: 4px 0 22px 0;
        }
        .sd-stat {
            background: #FFFFFF;
            border-radius: 18px;
            padding: 16px 18px;
            box-shadow: 0 4px 14px rgba(88, 101, 242, 0.12);
            border-left: 6px solid #5865F2;
        }
        .sd-stat.pink  { border-left-color: #EB459E; }
        .sd-stat.green { border-left-color: #1F9D55; }
        .sd-stat.amber { border-left-color: #E0A100; }
        .sd-stat .lbl {
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            color: #626B8A;
        }
        .sd-stat .val {
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -1px;
            color: #171A35;
            line-height: 1.1;
            margin-top: 4px;
        }

        /* One white card per subject */
        [class*="st-key-subj_"] {
            background: #FFFFFF !important;
            border: none !important;
            border-radius: 22px !important;
            box-shadow: 0 6px 18px rgba(88, 101, 242, 0.15) !important;
            padding: 20px 22px !important;
        }

        .sd-head {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 10px;
        }
        .sd-name {
            font-size: 22px;
            font-weight: 800;
            letter-spacing: -0.5px;
            color: #171A35;
            line-height: 1.2;
        }
        .sd-meta {
            margin-top: 8px;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .sd-chip {
            background: #EEF0FF;
            color: #3C46C8;
            border-radius: 999px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: 700;
        }
        .sd-chip.pink { background: #FFE7F3; color: #D91B87; }

        .sd-status {
            border-radius: 999px;
            padding: 5px 12px;
            font-size: 12px;
            font-weight: 800;
            white-space: nowrap;
        }
        .sd-status.good { background: #DDF5E6; color: #17713F; }
        .sd-status.warn { background: #FFF1CC; color: #8A6500; }
        .sd-status.low  { background: #FDE3E7; color: #B3263A; }
        .sd-status.none { background: #EEF0FF; color: #626B8A; }

        .sd-pct-row {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            margin: 18px 0 8px 0;
        }
        .sd-pct {
            font-size: 34px;
            font-weight: 800;
            letter-spacing: -1px;
            color: #171A35;
            line-height: 1;
        }
        .sd-pct-lbl {
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.7px;
            text-transform: uppercase;
            color: #626B8A;
        }
        .sd-bar {
            height: 10px;
            border-radius: 999px;
            background: #E6E8FA;
            overflow: hidden;
        }
        .sd-bar > span {
            display: block;
            height: 100%;
            border-radius: 999px;
        }
        .sd-mini {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin: 16px 0 12px 0;
        }
        .sd-mini div {
            background: #F5F6FF;
            border-radius: 14px;
            padding: 10px 12px;
            text-align: center;
        }
        .sd-mini b {
            display: block;
            font-size: 20px;
            font-weight: 800;
            color: #171A35;
        }
        .sd-mini span {
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            color: #626B8A;
        }

        .sd-empty {
            background: #FFFFFF;
            border-radius: 22px;
            padding: 40px 24px;
            text-align: center;
            box-shadow: 0 6px 18px rgba(88, 101, 242, 0.15);
        }
        .sd-empty .t {
            font-size: 22px;
            font-weight: 800;
            color: #171A35;
            letter-spacing: -0.5px;
        }
        .sd-empty .s {
            margin-top: 8px;
            font-size: 14px;
            color: #626B8A;
        }

        /* Text inside the unenroll popover (dark background) stays white */
        [data-testid="stPopoverBody"] p,
        [data-testid="stPopoverBody"] strong {
            color: #FFFFFF !important;
        }

        @media (max-width: 800px) {
            .sd-cards { grid-template-columns: repeat(2, 1fr); }
        }
        @media (max-width: 480px) {
            .sd-cards { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _sd_color(p):
    if p >= 75:
        return "#1F9D55"
    if p >= 50:
        return "#E0A100"
    return "#D93B4F"


def _sd_status(total, pct):
    if total == 0:
        return "none", "No classes yet"
    if pct >= 75:
        return "good", "Good standing"
    if pct >= 50:
        return "warn", "Needs attention"
    return "low", "Low attendance"


def _sd_stat_cards(items):
    out = ['<div class="sd-cards">']
    for label, value, cls in items:
        out.append(
            f'<div class="sd-stat {cls}"><div class="lbl">{escape(str(label))}</div>'
            f'<div class="val">{escape(str(value))}</div></div>'
        )
    out.append('</div>')
    return "".join(out)


def _sd_subject_html(sub, total, attended):
    missed = max(total - attended, 0)
    pct = (attended / total * 100) if total else 0
    status_cls, status_text = _sd_status(total, pct)
    color = _sd_color(pct) if total else "#C9CCEB"
    width = f"{pct:.0f}" if total else "0"
    pct_text = f"{pct:.0f}%" if total else "--"

    return "".join([
        '<div class="sd-head"><div>',
        f'<div class="sd-name">{escape(str(sub["name"]))}</div>',
        '<div class="sd-meta">',
        f'<span class="sd-chip">Code: {escape(str(sub["subject_code"]))}</span>',
        f'<span class="sd-chip pink">Section: {escape(str(sub["section"]))}</span>',
        '</div></div>',
        f'<span class="sd-status {status_cls}">{status_text}</span>',
        '</div>',
        '<div class="sd-pct-row">',
        f'<div class="sd-pct">{pct_text}</div>',
        '<div class="sd-pct-lbl">Attendance</div>',
        '</div>',
        f'<div class="sd-bar"><span style="width:{width}%;background:{color}"></span></div>',
        '<div class="sd-mini">',
        f'<div><b>{total}</b><span>Total</span></div>',
        f'<div><b>{attended}</b><span>Attended</span></div>',
        f'<div><b>{missed}</b><span>Missed</span></div>',
        '</div>',
    ])


def student_dashboard():
    student_data = st.session_state.student_data
    student_id = student_data['student_id']
    _sd_css()

    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {student_data['name']} """)
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.student_data
            st.rerun()

    st.space()

    h1, h2 = st.columns([3, 1], vertical_alignment='center')
    with h1:
        st.header('Your Enrolled Subjects')
    with h2:
        if st.button('Enroll in Subject', type='primary', width='stretch', icon=':material/add:'):
            enroll_dialog()

    st.divider()

    with st.spinner('Loading your enrolled subjects..'):
        subjects = get_student_subjects(student_id)
        logs = get_student_attendance(student_id)

    stats_map = {}

    for log in logs:
        sid = log['subject_id']

        if sid not in stats_map:
            stats_map[sid] = {"total": 0, "attended": 0}

        stats_map[sid]['total'] += 1

        if log.get('is_present'):
            stats_map[sid]['attended'] += 1

    if not subjects:
        st.markdown(
            '<div class="sd-empty"><div class="t">No subjects yet</div>'
            '<div class="s">Click <b>Enroll in Subject</b> and enter the code your teacher shared to join a class.</div></div>',
            unsafe_allow_html=True,
        )
        footer_dashboard()
        return

    # ---------------- Overall summary ----------------
    total_classes = sum(stats_map.get(n['subjects']['subject_id'], {}).get('total', 0) for n in subjects)
    total_attended = sum(stats_map.get(n['subjects']['subject_id'], {}).get('attended', 0) for n in subjects)
    overall = (total_attended / total_classes * 100) if total_classes else 0

    st.markdown(
        _sd_stat_cards([
            ("Subjects enrolled", len(subjects), ""),
            ("Total classes", total_classes, "pink"),
            ("Classes attended", total_attended, "green"),
            (
                "Overall attendance",
                f"{overall:.0f}%" if total_classes else "--",
                "green" if overall >= 75 else ("amber" if overall >= 50 else "pink"),
            ),
        ]),
        unsafe_allow_html=True,
    )

    # ---------------- Subject cards ----------------
    cols = st.columns(2, gap='large')
    for i, sub_node in enumerate(subjects):
        sub = sub_node['subjects']
        sid = sub['subject_id']
        stats = stats_map.get(sid, {"total": 0, "attended": 0})

        with cols[i % 2]:
            with st.container(border=True, key=f"subj_{sid}"):
                st.markdown(
                    _sd_subject_html(sub, stats['total'], stats['attended']),
                    unsafe_allow_html=True,
                )

                with st.popover(
                    "Unenroll from this course",
                    icon=':material/delete_forever:',
                    width='stretch',
                ):
                    st.markdown(f"Unenroll from **{escape(str(sub['name']))}**?")
                    st.markdown("You can join again later with the subject code.")
                    if st.button(
                        "Yes, unenroll me",
                        key=f"unenroll_{sid}",
                        type='primary',
                        width='stretch',
                    ):
                        unenroll_student_to_subject(student_id, sid)
                        st.toast(f"Unenrolled from {sub['name']} successfully!")
                        st.rerun()

            st.space()

    footer_dashboard()


def student_screen():

    style_background_dashboard()
    style_base_layout()
    style_student_screen()

    if "student_data" in st.session_state:
        student_dashboard()
        return

    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using FaceID', text_alignment='center')
    st.space()
    st.space()

    photo_source = st.camera_input("Position your face in the center")

    if photo_source is None:
        # Photo cleared: reset everything so the next scan starts fresh
        for k in ("scan_key", "scan_message", "show_registration"):
            st.session_state.pop(k, None)
    else:
        photo_bytes = photo_source.getvalue()
        scan_key = hash(photo_bytes)

        # Scan each new photo only once (reruns from typing a name must not re-scan)
        if st.session_state.get("scan_key") != scan_key:
            st.session_state.scan_key = scan_key
            st.session_state.scan_message = None
            st.session_state.show_registration = False

            img = np.array(Image.open(io.BytesIO(photo_bytes)).convert("RGB"))

            with st.spinner('AI is scanning..'):
                detected, all_ids, num_faces = predict_attendance(img)

                if num_faces == 0:
                    st.session_state.scan_message = ("warning", "Face not found!")
                elif num_faces > 1:
                    st.session_state.scan_message = ("warning", "Multiple faces found")
                else:
                    student = None
                    if detected:
                        # Compare as strings: the model may return "8" while the DB has 8
                        matched_id = str(list(detected.keys())[0])
                        all_students = get_all_students()
                        student = next(
                            (s for s in all_students if str(s['student_id']) == matched_id),
                            None,
                        )

                    if student:
                        st.session_state.is_logged_in = True
                        st.session_state.user_role = 'student'
                        st.session_state.student_data = student
                        st.toast(f"Welcome Back {student['name']}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        # Not recognized (or matched ID not in the database): offer registration
                        st.session_state.scan_message = (
                            "info",
                            "Face not recognized! You might be a new student - create your profile below.",
                        )
                        st.session_state.show_registration = True

        # Show the result of the scan (kept across reruns)
        msg = st.session_state.get("scan_message")
        if msg:
            getattr(st, msg[0])(msg[1])

    if st.session_state.get("show_registration") and photo_source is not None:
        with st.container(border=True):
            st.header('Register new Profile')
            new_name = st.text_input("Enter your name", placeholder='E.g. Harikesh Prajapati')

            st.subheader('Optional : Voice Enrollment')
            st.info("Enroll your voice for voice only attendance")

            audio_data = None

            try:
                audio_data = st.audio_input('Record a short phrase like I am present, My name is Harsh.')
            except Exception:
                st.error('Audio Data failed!')

            if st.button('Create Account', type='primary'):
                if new_name:
                    with st.spinner('Creating profile..'):
                        img = np.array(Image.open(io.BytesIO(photo_source.getvalue())).convert("RGB"))
                        encodings = get_face_embeddings(img)
                        if encodings:
                            face_emb = encodings[0].tolist()

                            voice_emb = None
                            if audio_data:
                                voice_emb = get_voice_embedding(audio_data.read())

                            response_data = create_student(new_name, face_embedding=face_emb, voice_embedding=voice_emb)

                            if response_data:
                                train_classifier()
                                st.session_state.is_logged_in = True
                                st.session_state.user_role = 'student'
                                st.session_state.student_data = response_data[0]
                                for k in ("scan_key", "scan_message", "show_registration"):
                                    st.session_state.pop(k, None)
                                st.toast(f"Profile Created! Hi {new_name}!")
                                time.sleep(1)
                                st.rerun()
                        else:
                            st.error('Couldnt capture your facial features for registration')

                else:
                    st.warning('Please enter your name!')

    footer_dashboard()







































