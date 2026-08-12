"""
Pure math calculator operations for the Student Grade System.
Contains GWA and academic status evaluation logic.
"""

from typing import List, Tuple, Optional

def calculate_weighted_average(grades_with_units: List[Tuple[float, float]]) -> Optional[float]:
    """
    Calculates the weighted average grade based on subject units.
    Formula: Sum(grade * units) / Sum(units)
    
    Args:
        grades_with_units: A list of tuples containing (numerical_grade, subject_units)
        
    Returns:
        The calculated weighted average rounded to 2 decimal places, or None if no grades are available.
    """
    if not grades_with_units:
        return None
        
    total_weighted_grades = 0.0
    total_units = 0.0
    
    for grade, units in grades_with_units:
        if units <= 0:
            raise ValueError("Subject units must be greater than zero for calculation.")
        total_weighted_grades += grade * units
        total_units += units
        
    if total_units == 0:
        return None
        
    return round(total_weighted_grades / total_units, 2)

def evaluate_academic_standing(weighted_average: Optional[float], subject_grades: List[float]) -> Tuple[str, str]:
    """
    Determines Pass/Fail status and Dean's Lister eligibility.
    
    Evaluation Rules:
    - Pass/Fail: "Passed" if average >= 75.0 AND no subject grade < 70.0; otherwise "Failed".
    - Dean's Lister: "Dean's Lister" if average >= 88.0 AND no subject grade < 80.0; otherwise "Not Eligible".
    
    Returns:
        A tuple of (pass_fail_status, deans_list_status)
    """
    if weighted_average is None or not subject_grades:
        return "Failed", "Not Eligible"
        
    # Check Pass/Fail
    has_failed_subject = any(grade < 70.0 for grade in subject_grades)
    if weighted_average >= 75.0 and not has_failed_subject:
        pass_fail_status = "Passed"
    else:
        pass_fail_status = "Failed"
        
    # Check Dean's Lister eligibility
    has_subject_below_dl_threshold = any(grade < 80.0 for grade in subject_grades)
    if weighted_average >= 88.0 and not has_subject_below_dl_threshold:
        deans_list_status = "Dean's Lister"
    else:
        deans_list_status = "Not Eligible"
        
    return pass_fail_status, deans_list_status
