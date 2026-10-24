import streamlit as st
from src.screens.database.db import create_subject

@st.dialog("Create New Subject")
def create_subject_dialog(teacher_id):
    st.write("Enter the details of new subject")
    sub_id = st.text_input("Subject Code", placeholder="CS101")
    sub_name = st.text_input("Subject Name", placeholder="Introduction to Computer Science")
    sub_section = st.text_input("Section", placeholder="A")


    if st.button("Create Subject Now", type='primary', width='stretch'):
        if sub_id and sub_name and sub_section:
            try:
                create_subject(sub_id, sub_name, sub_section, teacher_id)
                st.toast("Subject Created Succesfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.warning("Please fill all the fields")























# @st.dialog("Create New Subject")
# def create_subject_dialog(teacher_id):

#     # Make dialog title and input labels white
#     st.markdown("""
#         <style>
#         /* Dialog title */
#         div[data-testid="stDialog"] h2 {
#             color: white !important;
#         }

#         /* Subject Code, Subject Name, and Section labels */
#         div[data-testid="stDialog"] label {
#             color: white !important;
#             font-weight: 600 !important;
#         }
#         </style>
#     """, unsafe_allow_html=True)

#     st.write("Enter the details of new subject")

#     sub_id = st.text_input(
#         "Subject Code",
#         placeholder="ML101"
#     )

#     sub_name = st.text_input(
#         "Subject Name",
#         placeholder="Introduction to Machine Learning"
#     )

#     sub_section = st.text_input(
#         "Section",
#         placeholder="A"
#     )

#     if st.button(
#         "Create Subject Now",
#         type="primary",
#         width="stretch"
#     ):
#         if (
#             sub_id.strip()
#             and sub_name.strip()
#             and sub_section.strip()
#         ):
#             try:
#                 create_subject(
#                     sub_id.strip(),
#                     sub_name.strip(),
#                     sub_section.strip(),
#                     teacher_id
#                 )

#                 st.toast("Subject created successfully!")
#                 st.rerun()

#             except Exception as e:
#                 st.error(f"Error: {e}")

#         else:
#             st.warning("Please fill in all the fields.")






