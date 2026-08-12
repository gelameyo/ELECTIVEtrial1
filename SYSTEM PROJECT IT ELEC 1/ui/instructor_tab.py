"""
Instructor View module for the Student Grade System.
Contains forms for managing students, courses, recording grades, and classroom evaluation tables.
"""

import streamlit as st
import sqlite3
import database as db
import logic.validators as vl
import ui.components as sy

def render_instructor_dashboard(instructor_action: str) -> None:
    """
    Renders the instructor view options based on navigation input.
    """
    
    # Action 1: Grade Report
    if instructor_action == "📊 Grade Report":
        st.subheader("Class Academic Evaluation Report")
        
        # Search & Filters
        col_search, col_stats = st.columns([2, 1])
        
        with col_search:
            search_query = st.text_input("🔍 Search Student by ID, Name, or Program", "").strip().lower()
            
        all_evals = db.get_all_evaluations()
        
        # Apply Search Filter
        filtered_evals = []
        for e in all_evals:
            search_string = f"{e['student_id']} {e['first_name']} {e['last_name']} {e['program']}".lower()
            if not search_query or search_query in search_string:
                filtered_evals.append(e)
                
        # Metric Computations
        total_students = len(all_evals)
        total_passed = sum(1 for e in all_evals if e.get('pass_fail_status') == 'Passed')
        total_failed = sum(1 for e in all_evals if e.get('pass_fail_status') == 'Failed')
        total_deans = sum(1 for e in all_evals if e.get('deans_list_status') == "Dean's Lister")
        
        with col_stats:
            st.markdown(f"""
            <div style="display: flex; gap: 10px; justify-content: flex-end; padding-top: 1.5rem;">
                <span class="badge badge-info">Total: {total_students}</span>
                <span class="badge badge-passed">Passed: {total_passed}</span>
                <span class="badge badge-failed">Failed: {total_failed}</span>
                <span class="badge badge-deans">Deans: {total_deans}</span>
            </div>
            """, unsafe_allow_html=True)
            
        # Display Report Table
        if filtered_evals:
            st.markdown(sy.get_class_report_table_html(filtered_evals), unsafe_allow_html=True)
        else:
            st.info("No student evaluations match the search criteria.")
            
    # Action 2: Enter Grades
    elif instructor_action == "✍️ Enter Grades":
        st.subheader("Grade Entry Panel")
        
        students = db.get_all_students()
        subjects = db.get_all_subjects()
        
        if not students:
            st.warning("No students registered yet. Please add a student profile first.")
        elif not subjects:
            st.warning("No subjects added yet. Please register subjects first.")
        else:
            col_form, col_current = st.columns([1, 1])
            
            with col_form:
                st.markdown("""
                <div style="background-color: rgba(30, 41, 59, 0.4); padding: 1.5rem; border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.05);">
                    <h4 style="margin-top:0; color:#fff;">Record Grade</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # Student selector
                student_options = {f"{s['student_id']} - {s['last_name']}, {s['first_name']}": s['student_id'] for s in students}
                selected_student_label = st.selectbox("Select Student Profile:", list(student_options.keys()))
                selected_student_id = student_options[selected_student_label]
                
                # Subject selector
                subject_options = {f"{s['subject_code']} - {s['subject_name']}": s['subject_id'] for s in subjects}
                selected_subject_label = st.selectbox("Select Subject Course:", list(subject_options.keys()))
                selected_subject_id = subject_options[selected_subject_label]
                
                # Input grade
                numerical_grade = st.number_input(
                    "Numerical Grade (0.0 - 100.0):",
                    min_value=0.0,
                    max_value=100.0,
                    value=85.0,
                    step=0.5
                )
                
                if st.button("Save Grade Entry"):
                    try:
                        # Validation
                        vl.validate_grade(numerical_grade)
                        
                        # Save
                        db.upsert_grade(selected_student_id, selected_subject_id, numerical_grade)
                        st.success("Grade entry successfully logged and student GWA updated!")
                        st.rerun()
                    except ValueError as ve:
                        st.error(str(ve))
                    except Exception as e:
                        st.error(f"Error logging grade: {e}")
                        
            with col_current:
                st.markdown("<h4 style='color:#fff;'>Current Grade Records</h4>", unsafe_allow_html=True)
                student_grades = db.get_student_grades(selected_student_id)
                
                if student_grades:
                    st.write(f"Displaying grades for **{selected_student_label}**:")
                    st.markdown(sy.get_grades_table_html(student_grades), unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    delete_options = {f"Remove grade: {g['subject_code']} ({g['numerical_grade']})": g['grade_id'] for g in student_grades}
                    selected_delete_label = st.selectbox("Choose a grade record to delete (if needed):", ["-- Select grade to delete --"] + list(delete_options.keys()))
                    
                    if selected_delete_label != "-- Select grade to delete --":
                        delete_grade_id = delete_options[selected_delete_label]
                        if st.button("Confirm Delete Grade", type="secondary"):
                            try:
                                db.delete_grade(delete_grade_id, selected_student_id)
                                st.success("Grade record deleted and calculations refreshed.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting record: {e}")
                else:
                    st.info("No grades recorded for this student yet.")
                    
    # Action 3: Manage Students
    elif instructor_action == "👥 Manage Students":
        st.subheader("Student Profile Management")
        
        col_add, col_list = st.columns([1, 1])
        
        with col_add:
            st.markdown("<h4 style='color:#fff;'>Add Student Profile</h4>", unsafe_allow_html=True)
            
            with st.form("new_student_form", clear_on_submit=True):
                new_id = st.text_input("Student ID (e.g. 2026-0004):").strip()
                new_first = st.text_input("First Name:").strip()
                new_last = st.text_input("Last Name:").strip()
                new_program = st.text_input("Program / Course (e.g. BS Computer Science):").strip()
                
                submit_student = st.form_submit_button("Register Student")
                
                if submit_student:
                    try:
                        vl.validate_student_profile(new_id, new_first, new_last, new_program)
                        db.add_student(new_id, new_first, new_last, new_program)
                        st.success(f"Student profile registered: {new_first} {new_last}")
                        st.rerun()
                    except ValueError as ve:
                        st.error(str(ve))
                    except sqlite3.IntegrityError:
                        st.error("Registration Failed: A student with this ID already exists.")
                    except Exception as e:
                        st.error(f"Failed to add student: {e}")
                        
        with col_list:
            st.markdown("<h4 style='color:#fff;'>Active Student Directory</h4>", unsafe_allow_html=True)
            student_list = db.get_all_students()
            
            if student_list:
                for s in student_list:
                    col_det, col_del = st.columns([4, 1])
                    with col_det:
                        st.markdown(f"""
                        <div style="background: rgba(30, 41, 59, 0.3); border: 1px solid rgba(255, 255, 255, 0.05); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem;">
                            <strong>{s['last_name']}, {s['first_name']}</strong><br>
                            <small style="color: #94a3b8;">ID: {s['student_id']} | {s['program']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_del:
                        if st.button("Delete ❌", key=f"del_stud_{s['student_id']}"):
                            try:
                                db.delete_student(s['student_id'])
                                st.success(f"Deleted profile: {s['student_id']}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
            else:
                st.info("No student profiles found.")
                
    # Action 4: Manage Subjects
    elif instructor_action == "📚 Manage Subjects":
        st.subheader("Subject Directory Settings")
        
        col_add_sub, col_list_sub = st.columns([1, 1])
        
        with col_add_sub:
            st.markdown("<h4 style='color:#fff;'>Register Subject Course</h4>", unsafe_allow_html=True)
            
            with st.form("new_subject_form", clear_on_submit=True):
                sub_code = st.text_input("Subject Code (e.g. CS103):").strip()
                sub_name = st.text_input("Subject Course Name:").strip()
                sub_units = st.number_input("Credit Units:", min_value=0.5, max_value=6.0, value=3.0, step=0.5)
                
                submit_subject = st.form_submit_button("Register Subject")
                
                if submit_subject:
                    try:
                        vl.validate_subject_details(sub_code, sub_name, sub_units)
                        db.add_subject(sub_code, sub_name, sub_units)
                        st.success(f"Subject Course registered: {sub_code} - {sub_name}")
                        st.rerun()
                    except ValueError as ve:
                        st.error(str(ve))
                    except sqlite3.IntegrityError:
                        st.error("Registration Failed: A subject with this code already exists.")
                    except Exception as e:
                        st.error(f"Failed to add subject: {e}")
                        
        with col_list_sub:
            st.markdown("<h4 style='color:#fff;'>Available Subjects Directory</h4>", unsafe_allow_html=True)
            sub_list = db.get_all_subjects()
            
            if sub_list:
                for s in sub_list:
                    col_det, col_del = st.columns([4, 1])
                    with col_det:
                        st.markdown(f"""
                        <div style="background: rgba(30, 41, 59, 0.3); border: 1px solid rgba(255, 255, 255, 0.05); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem;">
                            <strong>{s['subject_code']} - {s['subject_name']}</strong><br>
                            <small style="color: #94a3b8;">Credits: {s['units']:.1f} Units</small>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_del:
                        if st.button("Delete ❌", key=f"del_sub_{s['subject_id']}"):
                            try:
                                db.delete_subject(s['subject_id'])
                                st.success(f"Deleted course: {s['subject_code']}")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error: {e}")
            else:
                st.info("No subject courses found.")
