"""
Validator rules for Student Grade System input fields.
"""

def validate_student_profile(student_id: str, first_name: str, last_name: str, program: str) -> None:
    """
    Validates student profile fields.
    Raises ValueError if any field is invalid.
    """
    if not student_id or not student_id.strip():
        raise ValueError("Student ID cannot be empty.")
    if not first_name or not first_name.strip():
        raise ValueError("First name cannot be empty.")
    if not last_name or not last_name.strip():
        raise ValueError("Last name cannot be empty.")
    if not program or not program.strip():
        raise ValueError("Program/Course cannot be empty.")

def validate_subject_details(subject_code: str, subject_name: str, units: float) -> None:
    """
    Validates subject fields.
    Raises ValueError if any field is invalid.
    """
    if not subject_code or not subject_code.strip():
        raise ValueError("Subject code cannot be empty.")
    if not subject_name or not subject_name.strip():
        raise ValueError("Subject name cannot be empty.")
    if units <= 0:
        raise ValueError("Subject units must be greater than zero.")

def validate_grade(grade: float) -> None:
    """
    Validates if the numerical grade is between 0.0 and 100.0.
    Raises ValueError if invalid.
    """
    try:
        val = float(grade)
    except (ValueError, TypeError):
        raise ValueError("Grade must be a valid numerical value.")
    
    if val < 0.0 or val > 100.0:
        raise ValueError("Grade must be between 0.0 and 100.0 inclusive.")
