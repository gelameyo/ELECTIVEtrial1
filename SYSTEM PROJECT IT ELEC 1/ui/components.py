"""
HTML Component templates for Student Grade System.
Contains functions that generate raw HTML strings for beautiful layouts, badges, and lists.
"""

from typing import List, Dict, Any, Optional

def get_header_html(title: str, subtitle: str) -> str:
    """
    Returns an HTML block for a premium dashboard header.
    """
    return f"""
    <div style="background: linear-gradient(135deg, #312e81 0%, #1e1b4b 100%); 
                padding: 2rem; border-radius: 16px; margin-bottom: 2rem; 
                border: 1px solid rgba(255, 255, 255, 0.08); 
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);">
        <h1 style="color: #ffffff; font-weight: 700; margin: 0; font-size: 2.2rem; 
                   letter-spacing: -0.02em;">{title}</h1>
        <p style="color: #a5b4fc; font-weight: 400; margin: 0.5rem 0 0 0; font-size: 1.1rem;">{subtitle}</p>
    </div>
    """

def get_student_dashboard_card_html(student_info: dict, evaluation: Optional[dict]) -> str:
    """
    Renders the custom HTML dashboard displaying student profile metrics:
    - GWA (General Weighted Average)
    - Pass/Fail Badge
    - Dean's Lister Status Card
    """
    first_name = student_info.get("first_name", "")
    last_name = student_info.get("last_name", "")
    student_id = student_info.get("student_id", "")
    program = student_info.get("program", "")
    
    if evaluation:
        gwa_val = f"{evaluation['calculated_average']:.2f}"
        
        # Pass Fail
        if evaluation['pass_fail_status'] == "Passed":
            pass_status_class = "stat-passed"
            pass_status_label = "Passed"
            pass_status_desc = "Meets or exceeds 75.0 average"
        else:
            pass_status_class = "stat-failed"
            pass_status_label = "Failed"
            pass_status_desc = "Average below 75.0 or a subject below 70.0"
            
        # Dean's Lister
        if evaluation['deans_list_status'] == "Dean's Lister":
            dl_class = "stat-deans"
            dl_label = "Dean's Lister"
            dl_desc = "Eligible: GWA >= 88.0 & no subject < 80.0"
        else:
            dl_class = "stat-not-eligible"
            dl_label = "Not Eligible"
            dl_desc = "DL criteria not met"
    else:
        gwa_val = "N/A"
        pass_status_class = "stat-not-eligible"
        pass_status_label = "No Grades"
        pass_status_desc = "No subject grades logged yet"
        
        dl_class = "stat-not-eligible"
        dl_label = "No Grades"
        dl_desc = "No subject grades logged yet"

    return f"""
    <div class="dashboard-container">
        <div style="display: flex; justify-content: space-between; align-items: center; 
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 1rem; margin-bottom: 1.5rem;">
            <div>
                <h2 style="margin: 0; color: #ffffff; font-size: 1.6rem; font-weight: 600;">{first_name} {last_name}</h2>
                <div style="color: #94a3b8; font-size: 0.95rem; margin-top: 0.2rem;">{program}</div>
            </div>
            <div style="text-align: right;">
                <span class="badge badge-info" style="font-size: 0.85rem; padding: 0.4rem 1rem;">ID: {student_id}</span>
            </div>
        </div>
        
        <div class="stats-grid">
            <!-- GWA Metric Card -->
            <div class="stat-card stat-gwa">
                <div class="stat-label">General Weighted Average</div>
                <div class="stat-value" style="color: #818cf8;">{gwa_val}</div>
                <div class="stat-desc">Calculated based on credit units</div>
            </div>
            
            <!-- Academic Standing Card -->
            <div class="stat-card {pass_status_class}">
                <div class="stat-label">Academic Standing</div>
                <div class="stat-value-text" style="color: { '#34d399' if pass_status_label == 'Passed' else '#f87171' if pass_status_label == 'Failed' else '#94a3b8' }; margin-top: 0.5rem; margin-bottom: 0.5rem;">
                    {pass_status_label}
                </div>
                <div class="stat-desc">{pass_status_desc}</div>
            </div>
            
            <!-- Dean's Lister Eligibility Card -->
            <div class="stat-card {dl_class}">
                <div class="stat-label">Dean's Lister Eligibility</div>
                <div class="stat-value-text" style="color: { '#fbbf24' if dl_label == 'Dean\\'s Lister' else '#94a3b8' }; margin-top: 0.5rem; margin-bottom: 0.5rem;">
                    {dl_label}
                </div>
                <div class="stat-desc">{dl_desc}</div>
            </div>
        </div>
    </div>
    """

def get_grades_table_html(grades: list) -> str:
    """
    Renders an HTML grade table layout with custom CSS styles.
    """
    if not grades:
        return """
        <div style="text-align: center; padding: 2rem; color: #64748b; background: rgba(30, 41, 59, 0.4); border-radius: 12px;">
            No grades recorded for this student yet.
        </div>
        """
        
    rows_html = ""
    for idx, g in enumerate(grades):
        num_grade = g['numerical_grade']
        # Remark styling
        if num_grade >= 75.0:
            remark = "Passed"
            badge_class = "badge-passed"
        else:
            remark = "Failed"
            badge_class = "badge-failed"
            
        rows_html += f"""
        <tr>
            <td style="font-weight: 500;">{g['subject_code']}</td>
            <td>{g['subject_name']}</td>
            <td style="text-align: center;">{g['units']:.1f}</td>
            <td style="text-align: right; font-weight: 600; color: #ffffff;">{num_grade:.2f}</td>
            <td style="text-align: center;"><span class="badge {badge_class}">{remark}</span></td>
        </tr>
        """
        
    return f"""
    <div class="table-responsive">
        <table class="custom-table">
            <thead>
                <tr>
                    <th style="width: 15%;">Subject Code</th>
                    <th style="width: 45%;">Subject Name</th>
                    <th style="width: 15%; text-align: center;">Units</th>
                    <th style="width: 15%; text-align: right;">Numerical Grade</th>
                    <th style="width: 10%; text-align: center;">Remark</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """

def get_class_report_table_html(evaluations: list) -> str:
    """
    Renders the custom HTML table for class summaries (Instructor view).
    """
    if not evaluations:
        return """
        <div style="text-align: center; padding: 2rem; color: #64748b; background: rgba(30, 41, 59, 0.4); border-radius: 12px;">
            No students added yet.
        </div>
        """
        
    rows_html = ""
    for e in evaluations:
        gwa_val = f"{e['calculated_average']:.2f}" if e['calculated_average'] is not None else "N/A"
        
        # Standing badge
        pass_status = e['pass_fail_status'] or "N/A"
        if pass_status == "Passed":
            pass_badge = '<span class="badge badge-passed">Passed</span>'
        elif pass_status == "Failed":
            pass_badge = '<span class="badge badge-failed">Failed</span>'
        else:
            pass_badge = '<span class="badge badge-not-eligible">-</span>'
            
        # DL badge
        dl_status = e['deans_list_status'] or "N/A"
        if dl_status == "Dean's Lister":
            dl_badge = '<span class="badge badge-deans">Dean\'s Lister</span>'
        elif dl_status == "Not Eligible":
            dl_badge = '<span class="badge badge-not-eligible">Not Eligible</span>'
        else:
            dl_badge = '<span class="badge badge-not-eligible">-</span>'
            
        rows_html += f"""
        <tr>
            <td style="font-weight: 500;">{e['student_id']}</td>
            <td style="font-weight: 500; color: #ffffff;">{e['last_name']}, {e['first_name']}</td>
            <td>{e['program']}</td>
            <td style="text-align: right; font-weight: 600; color: #818cf8;">{gwa_val}</td>
            <td style="text-align: center;">{pass_badge}</td>
            <td style="text-align: center;">{dl_badge}</td>
        </tr>
        """
        
    return f"""
    <div class="table-responsive">
        <table class="custom-table">
            <thead>
                <tr>
                    <th style="width: 15%;">Student ID</th>
                    <th style="width: 25%;">Student Name</th>
                    <th style="width: 25%;">Program</th>
                    <th style="width: 10%; text-align: right;">GWA</th>
                    <th style="width: 10%; text-align: center;">Standing</th>
                    <th style="width: 15%; text-align: center;">Dean's Lister</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """
