"""
Student Grade & Academic Evaluation System
Main application entry point. Loads configurations, stylesheets, brand assets, and dispatches views.
"""

import os
import streamlit as st
import database as db
import ui
import ui.components as sy

# 1. Page Configuration Setup
st.set_page_config(
    page_title="Academic Grade & Evaluation System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Database Initialization
try:
    db.init_db()
except Exception as e:
    st.error(f"Failed to initialize database: {e}")

# 3. Load External CSS Stylesheet
css_path = os.path.join("static", "css", "styles.css")
if os.path.exists(css_path):
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load custom styles: {e}")

# 4. Sidebar Branding & Navigation
logo_path = os.path.join("static", "images", "logo.png")
if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h2 style="color: #6366f1; font-weight: 700; margin-bottom: 0;">🎓 GradeSys</h2>
        <small style="color: #64748b;">Academic Evaluation Portal</small>
    </div>
    """, unsafe_allow_html=True)

actor_role = st.sidebar.selectbox(
    "Choose User Role:",
    ["Instructor Dashboard", "Student Dashboard"],
    index=0
)

# 5. Route views based on Selected Role
if actor_role == "Instructor Dashboard":
    st.markdown(sy.get_header_html(
        "Instructor Portal", 
        "Manage students, subject profiles, enter grades, and view evaluations."
    ), unsafe_allow_html=True)
    
    instructor_action = st.sidebar.radio(
        "Navigation Tasks:",
        [
            "📊 Grade Report",
            "✍️ Enter Grades",
            "👥 Manage Students",
            "📚 Manage Subjects"
        ]
    )
    
    # Delegate rendering to ui package
    ui.render_instructor_dashboard(instructor_action)

else:
    st.markdown(sy.get_header_html(
        "Student Grades Portal", 
        "Check your current grades, overall weighted average, and academic standing."
    ), unsafe_allow_html=True)
    
    # Delegate rendering to ui package
    ui.render_student_dashboard()
