"""
Student View module for the Student Grade System.
Allows students to query their profile and displays their grades dashboard.
"""

import streamlit as st
import database as db
import ui.components as sy

def render_student_dashboard() -> None:
    """
    Renders the student search view, card dashboards, and subject breakdown reports.
    """
    students = db.get_all_students()
    
    if not students:
        st.info("No student profiles registered in the system. Please consult your administrator.")
    else:
        student_options = {f"{s['student_id']} - {s['last_name']}, {s['first_name']}": s['student_id'] for s in students}
        
        col_search_stud, _ = st.columns([2, 2])
        with col_search_stud:
            selected_student_lbl = st.selectbox("Select Student Profile to View Summary:", list(student_options.keys()))
            selected_student_id = student_options[selected_student_lbl]
            
        student_info = db.get_student(selected_student_id)
        evaluation = db.get_student_evaluation(selected_student_id)
        grades = db.get_student_grades(selected_student_id)
        
        if student_info:
            # Render visual student header and card dashboard
            st.markdown(sy.get_student_dashboard_card_html(student_info, evaluation), unsafe_allow_html=True)
            
            # Render grades breakdown sheet
            st.markdown("<h3 style='margin-top:2rem; color:#fff;'>Academic Grades Breakdown</h3>", unsafe_allow_html=True)
            st.markdown(sy.get_grades_table_html(grades), unsafe_allow_html=True)
        else:
            st.error("Error retrieving student profile information.")
