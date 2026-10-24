import time
from html import escape
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

from src.screens.ui.base_layout import (
    style_background_dashboard,
    style_base_layout,
)
from src.screens.components.header import header_dashboard
from src.screens.components.footer import footer_dashboard
from src.screens.components.subject_card import subject_card
from src.screens.components.dialog_add_photo import add_photos_dialog
from src.screens.components.dialog_create_subject import create_subject_dialog
from src.screens.components.dialog_share_subject import share_subject_dialog
from src.screens.components.dialog_attendance_results import (
    attendance_result_dialog,
)
from src.screens.components.dialog_voice_attendance import (
    voice_attendance_dialog,
)

from src.screens.database.config import supabase
from src.screens.database.db import (
    check_teacher_exists,
    create_teacher,
    teacher_login,
    get_teacher_subjects,
    get_attendance_for_teacher,
)
from PIPELINE.face_pipeline import predict_attendance


def style_teacher_screen():
    """Inter font for the title/headings and black headings + input labels."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        /* ---------- Inter font: "Apani Hazari" title, headings, labels ---------- */
        [data-testid="stMarkdownContainer"] *:not([data-testid="stIconMaterial"]),
        [data-testid="stHtml"] *,
        [data-testid="stHeading"],
        [data-testid="stHeading"] *,
        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] *,
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

        /* ---------- Black headings: "Login using password", etc. ---------- */
        [data-testid="stHeading"],
        [data-testid="stHeading"] * {
            color: #000000 !important;
            font-weight: 800 !important;
            letter-spacing: -0.5px !important;
        }

        /* ---------- Black input labels: "Enter username", "Enter password" ---------- */
        [data-testid="stWidgetLabel"],
        [data-testid="stWidgetLabel"] *,
        label,
        label * {
            color: #000000 !important;
            font-weight: 600 !important;
        }

        /* ---------- Metrics (Total classes held, Attended, ...) in black ---------- */
        [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] *,
        [data-testid="stMetricValue"],
        [data-testid="stMetricValue"] * {
            color: #000000 !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* ---------- Photo captions ("Photo 1", "Photo 2") in black ---------- */
        [data-testid="stImageCaption"],
        [data-testid="stImageCaption"] *,
        [data-testid="stCaptionContainer"],
        [data-testid="stCaptionContainer"] * {
            color: #000000 !important;
            font-family: 'Inter', sans-serif !important;
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
        div[role="dialog"] label * {
            color: #FFFFFF !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def teacher_screen():

    style_background_dashboard()
    style_base_layout()
    style_teacher_screen()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type == "login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()


def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {teacher_data['name']} """)
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data
            st.rerun()

    st.space()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'
    tab1, tab2, tab3 = st.columns(3)

    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendance' else "tertiary"
        if st.button('Take Attendance', type=type1, width='stretch', icon=':material/ar_on_you:'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "tertiary"
        if st.button('Manage Subjects', type=type2, width='stretch', icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendance_records' else "tertiary"
        if st.button('Attendance Records', type=type3, width='stretch', icon=':material/cards_stack:'):
            st.session_state.current_teacher_tab = 'attendance_records'
            st.rerun()

    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendance()
    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == "attendance_records":
        teacher_tab_attendance_records()

    footer_dashboard()


def teacher_tab_take_attendance():
    teacher_id = st.session_state.teacher_data['teacher_id']
    st.header('Take AI Attendance')

    if 'attendance_images' not in st.session_state:
        st.session_state.attendance_images = []

    subjects = get_teacher_subjects(teacher_id)

    if not subjects:
        st.warning('You havent created any subjects yet! Please create one to begin!')
        return

    subject_options = {f"{s['name']} - {s['subject_code']}": s['subject_id'] for s in subjects}

    col1, col2 = st.columns([3, 1], vertical_alignment='bottom')

    with col1:
        selected_subject_label = st.selectbox('Select Subject', options=list(subject_options.keys()))

    with col2:
        if st.button('Add Photos', type='primary', icon=':material/photo_prints:', width='stretch'):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]

    st.divider()

    if st.session_state.attendance_images:
        st.header('Added Photos')
        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendance_images):
            with gallery_cols[idx % 4]:
                st.image(img, width='stretch', caption=f'Photo {idx+1}')
    has_photos = bool(st.session_state.attendance_images)
    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button('Clear all photos', width='stretch', type='tertiary', icon=':material/delete:', disabled=not has_photos):
            st.session_state.attendance_images = []
            st.rerun()

    with c2:

        if st.button('Run Face Analysis', width='stretch', type='secondary', icon=':material/analytics:', disabled=not has_photos):
            with st.spinner('Deep scanning classroom photos...'):
                all_detected_ids = {}

                for idx, img in enumerate(st.session_state.attendance_images):
                    img_np = np.array(img.convert('RGB'))
                    detected, _, _ = predict_attendance(img_np)

                    if detected:
                        for sid in detected.keys():
                            student_id = int(sid)

                            all_detected_ids.setdefault(student_id, []).append(f"Photo {idx+1}")

                enrolled_res = supabase.table('subject_students').select("*, students(*)").eq('subject_id', selected_subject_id).execute()
                enrolled_students = enrolled_res.data

                if not enrolled_students:
                    st.warning('No students enrolled in this course')
                else:

                    results, attendance_to_log = [], []

                    current_timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                    for node in enrolled_students:
                        student = node['students']
                        sources = all_detected_ids.get(int(student['student_id']), [])
                        is_present = len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources) if is_present else "-",
                            "Status": "✅ Present" if is_present else "❌ Absent"
                        })

                        attendance_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                    attendance_result_dialog(pd.DataFrame(results), attendance_to_log)

    with c3:
        if st.button('Use Voice Attendance', type='primary', width='stretch', icon=':material/mic:'):
            voice_attendance_dialog(selected_subject_id)


def teacher_tab_manage_subjects():
    teacher_id = st.session_state.teacher_data['teacher_id']
    col1, col2 = st.columns(2)
    with col1:
        st.header('Manage Subjects', width='stretch')

    with col2:
        if st.button('Create New Subject', width='stretch'):
            create_subject_dialog(teacher_id)

    # LIST all SUBJECTS
    subjects = get_teacher_subjects(teacher_id)
    if subjects:
        for sub in subjects:
            stats = [
                ("🫂", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes']),
            ]

            def share_btn(sub=sub):
                if st.button(f"Share Code: {sub['name']}", key=f"share_{sub['subject_code']}", icon=":material/share:"):
                    share_subject_dialog(sub['name'], sub['subject_code'])
                st.space()

            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=stats,
                footer_callback=share_btn
            )
    else:
        st.info("NO SUBJECTS FOUND. CREATE ONE ABOVE")


def _records_css():
    st.markdown(
        """
        <style>
        .rec-cards {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin: 6px 0 18px 0;
        }
        .rec-card {
            background: #FFFFFF;
            border-radius: 18px;
            padding: 16px 18px;
            box-shadow: 0 4px 14px rgba(88, 101, 242, 0.12);
            border-left: 6px solid #5865F2;
        }
        .rec-card.pink  { border-left-color: #EB459E; }
        .rec-card.green { border-left-color: #1F9D55; }
        .rec-card.amber { border-left-color: #E0A100; }
        .rec-card .lbl {
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            color: #626B8A;
        }
        .rec-card .val {
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -1px;
            color: #171A35;
            line-height: 1.1;
            margin-top: 4px;
        }

        .rec-wrap {
            background: #FFFFFF;
            border-radius: 18px;
            overflow-x: auto;
            box-shadow: 0 4px 14px rgba(88, 101, 242, 0.12);
            margin-bottom: 8px;
        }
        table.rec-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        table.rec-table th {
            background: #EEF0FF;
            color: #626B8A;
            text-align: left;
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.7px;
            text-transform: uppercase;
            padding: 12px 16px;
            white-space: nowrap;
        }
        table.rec-table td {
            color: #171A35;
            padding: 12px 16px;
            border-bottom: 1px solid #EEF0FF;
            white-space: nowrap;
            font-weight: 500;
        }
        table.rec-table tr:last-child td { border-bottom: none; }
        table.rec-table tr:hover td { background: #F7F8FF; }

        .rec-no {
            display: inline-block;
            min-width: 30px;
            text-align: center;
            padding: 3px 10px;
            border-radius: 999px;
            background: #E0E3FF;
            color: #3C46C8;
            font-weight: 800;
            font-size: 13px;
        }
        .rec-bar {
            display: inline-block;
            vertical-align: middle;
            width: 110px;
            height: 9px;
            border-radius: 999px;
            background: #E6E8FA;
            overflow: hidden;
        }
        .rec-bar > span {
            display: block;
            height: 100%;
            border-radius: 999px;
        }
        .rec-pct {
            display: inline-block;
            min-width: 44px;
            margin-left: 10px;
            font-weight: 800;
            color: #171A35;
        }

        .rec-pill {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 700;
        }
        .rec-pill.present { background: #DDF5E6; color: #17713F; }
        .rec-pill.absent  { background: #FDE3E7; color: #B3263A; }
        .rec-pill-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 6px 0 14px 0;
        }

        .rec-line, .rec-line * {
            color: #000000 !important;
            font-weight: 600;
            font-size: 15px;
        }
        .rec-line { margin: 10px 0 2px 0; }

        /* Tabs: black labels (inactive), pink (active) */
        [data-testid="stTabs"] button,
        [data-testid="stTabs"] button *,
        [data-testid="stTab"],
        [data-testid="stTab"] *,
        button[data-baseweb="tab"],
        button[data-baseweb="tab"] *,
        [data-baseweb="tab-list"] button,
        [data-baseweb="tab-list"] button * {
            color: #000000 !important;
            opacity: 1 !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 700 !important;
            font-size: 15px !important;
        }
        [data-testid="stTabs"] button[aria-selected="true"],
        [data-testid="stTabs"] button[aria-selected="true"] *,
        button[data-baseweb="tab"][aria-selected="true"],
        button[data-baseweb="tab"][aria-selected="true"] *,
        [data-baseweb="tab-list"] button[aria-selected="true"],
        [data-baseweb="tab-list"] button[aria-selected="true"] * {
            color: #D91B87 !important;
        }

        @media (max-width: 700px) {
            .rec-cards { grid-template-columns: 1fr; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _pct_color(p):
    if p >= 75:
        return "#1F9D55"
    if p >= 50:
        return "#E0A100"
    return "#D93B4F"


def _bar_html(p):
    p = max(0, min(100, float(p)))
    return (
        f'<span class="rec-bar"><span style="width:{p:.0f}%;background:{_pct_color(p)}"></span></span>'
        f'<span class="rec-pct">{p:.0f}%</span>'
    )


def _cards_html(items):
    """items: list of (label, value, color_class)."""
    out = ['<div class="rec-cards">']
    for label, value, cls in items:
        out.append(
            f'<div class="rec-card {cls}"><div class="lbl">{escape(str(label))}</div>'
            f'<div class="val">{escape(str(value))}</div></div>'
        )
    out.append('</div>')
    return "".join(out)


def _table_html(headers, rows):
    """rows: list of lists of ready-made HTML strings."""
    head = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="rec-wrap"><table class="rec-table"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def teacher_tab_attendance_records():
    st.header('Attendance Records')
    _records_css()

    teacher_id = st.session_state.teacher_data['teacher_id']

    records = get_attendance_for_teacher(teacher_id)

    if not records:
        st.info('No attendance has been taken yet.')
        return

    # If the records don't include student details, look the names up.
    student_names = {}
    if any(not r.get('students') for r in records):
        try:
            res = supabase.table('students').select('student_id, name').execute()
            student_names = {s['student_id']: s['name'] for s in res.data}
        except Exception:
            student_names = {}

    rows = []
    for r in records:
        ts = r.get('timestamp')
        if not ts:
            continue
        dt = pd.to_datetime(ts, errors='coerce')
        if pd.isna(dt):
            continue

        sid = r.get('student_id')
        student = r.get('students') or {}
        name = student.get('name') or student_names.get(sid) or f"Student {sid}"

        rows.append({
            "class_key": ts.split(".")[0],
            "Date": dt.strftime("%d %b %Y"),
            "Time": dt.strftime("%I:%M %p"),
            "Subject": r['subjects']['name'],
            "Subject Code": r['subjects']['subject_code'],
            "student_id": sid,
            "Student": name,
            "is_present": bool(r.get('is_present', False)),
        })

    if not rows:
        st.info('No attendance has been taken yet.')
        return

    df = pd.DataFrame(rows)
    df["Subject Label"] = df["Subject"] + " - " + df["Subject Code"]

    # ---------------- Subject picker ----------------
    subject_labels = sorted(df["Subject Label"].unique())
    selected_label = st.selectbox('Select Subject', options=subject_labels, key='records_subject')
    sdf = df[df["Subject Label"] == selected_label]

    # ---------------- Classes held (one row per class session) ----------------
    classes = (
        sdf.groupby(['class_key', 'Date', 'Time'])
        .agg(Present=('is_present', 'sum'), Total=('is_present', 'count'))
        .reset_index()
        .sort_values('class_key')
        .reset_index(drop=True)
    )
    classes['Class No'] = classes.index + 1
    classes['Pct'] = classes['Present'] / classes['Total'] * 100

    # ---------------- Student-wise totals ----------------
    per_student = (
        sdf.groupby(['student_id', 'Student'])
        .agg(Attended=('is_present', 'sum'), Total=('is_present', 'count'))
        .reset_index()
    )
    per_student['Absent'] = per_student['Total'] - per_student['Attended']
    per_student['Pct'] = per_student['Attended'] / per_student['Total'] * 100
    per_student = per_student.sort_values('Student').reset_index(drop=True)

    avg_pct = per_student['Pct'].mean()

    # ---------------- Summary cards ----------------
    st.markdown(
        _cards_html([
            ("Total classes held", len(classes), ""),
            ("Students", len(per_student), "pink"),
            ("Average attendance", f"{avg_pct:.0f}%",
             "green" if avg_pct >= 75 else ("amber" if avg_pct >= 50 else "pink")),
        ]),
        unsafe_allow_html=True,
    )

    tab_classes, tab_students, tab_detail = st.tabs(
        ["📅 Classes held", "👥 Student-wise", "🔎 Student details"]
    )

    # ---------------- 1) All classes held ----------------
    with tab_classes:
        html_rows = []
        for _, c in classes.sort_values('class_key', ascending=False).iterrows():
            html_rows.append([
                f'<span class="rec-no">{int(c["Class No"])}</span>',
                escape(c['Date']),
                escape(c['Time']),
                f'{int(c["Present"])} / {int(c["Total"])} students',
                _bar_html(c['Pct']),
            ])
        st.markdown(
            _table_html(['Class', 'Date', 'Time', 'Present', 'Attendance'], html_rows),
            unsafe_allow_html=True,
        )

    # ---------------- 2) Student-wise attendance ----------------
    with tab_students:
        html_rows = []
        for _, s in per_student.iterrows():
            html_rows.append([
                f'<b>{escape(str(s["Student"]))}</b>',
                escape(str(s['student_id'])),
                f'{int(s["Attended"])} / {int(s["Total"])}',
                str(int(s['Absent'])),
                _bar_html(s['Pct']),
            ])
        st.markdown(
            _table_html(['Student', 'ID', 'Attended / Total', 'Absent', 'Attendance'], html_rows),
            unsafe_allow_html=True,
        )

    # ---------------- 3) One student's class-by-class detail ----------------
    with tab_detail:
        student_options = {
            f"{row['Student']} (ID: {row['student_id']})": row['student_id']
            for _, row in per_student.iterrows()
        }
        chosen = st.selectbox('Select Student', options=list(student_options.keys()), key='records_student')
        chosen_id = student_options[chosen]

        stu = sdf[sdf['student_id'] == chosen_id].merge(
            classes[['class_key', 'Class No']], on='class_key', how='left'
        ).sort_values('class_key')

        attended = int(stu['is_present'].sum())
        total = int(len(stu))
        pct = (attended / total * 100) if total else 0

        st.markdown(
            _cards_html([
                ("Classes held", total, ""),
                ("Attended", attended, "green"),
                ("Attendance", f"{pct:.0f}%",
                 "green" if pct >= 75 else ("amber" if pct >= 50 else "pink")),
            ]),
            unsafe_allow_html=True,
        )

        def pills(frame, css):
            return '<div class="rec-pill-wrap">' + "".join(
                f'<span class="rec-pill {css}">Class {int(r["Class No"])} · {escape(r["Date"])} · {escape(r["Time"])}</span>'
                for _, r in frame.iterrows()
            ) + '</div>'

        present_df = stu[stu['is_present']]
        absent_df = stu[~stu['is_present']]

        st.markdown('<div class="rec-line"><b>Attended on:</b></div>', unsafe_allow_html=True)
        if len(present_df):
            st.markdown(pills(present_df, 'present'), unsafe_allow_html=True)
        else:
            st.markdown('<div class="rec-line">No classes attended yet</div>', unsafe_allow_html=True)

        if len(absent_df):
            st.markdown('<div class="rec-line"><b>Missed on:</b></div>', unsafe_allow_html=True)
            st.markdown(pills(absent_df, 'absent'), unsafe_allow_html=True)

        st.markdown('<div class="rec-line"><b>Class-by-class</b></div>', unsafe_allow_html=True)
        html_rows = []
        for _, r in stu.sort_values('class_key', ascending=False).iterrows():
            ok = bool(r['is_present'])
            badge = (
                '<span class="rec-pill present">✅ Present</span>' if ok
                else '<span class="rec-pill absent">❌ Absent</span>'
            )
            html_rows.append([
                f'<span class="rec-no">{int(r["Class No"])}</span>',
                escape(r['Date']),
                escape(r['Time']),
                badge,
            ])
        st.markdown(
            _table_html(['Class', 'Date', 'Time', 'Status'], html_rows),
            unsafe_allow_html=True,
        )


def login_teacher(username, password):
    if not username or not password:
        return False

    teacher = teacher_login(username, password)

    if teacher:
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True

    return False


def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using password', text_alignment='center')
    st.space()
    st.space()

    teacher_username = st.text_input("Enter username", placeholder='Harsh Prajapati')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Login', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("welcome back!", icon="👋")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username and password combo")

    with btnc2:
        if st.button('Register Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'register'

    footer_dashboard()


def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All Fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "Username already taken"
    if teacher_pass != teacher_pass_confirm:
        return False, "Password doesn't match"

    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Sucessfully Created! Login Now"
    except Exception as e:
        return False, "Unexpected Error!"


def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Register your teacher profile')

    st.space()
    st.space()

    teacher_username = st.text_input("Enter username", placeholder='ananyaroy')

    teacher_name = st.text_input("Enter name", placeholder='Ananya Roy')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Register now', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)

    with btnc2:
        if st.button('Login Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'login'

    footer_dashboard()


















