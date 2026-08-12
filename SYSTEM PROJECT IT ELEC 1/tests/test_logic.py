"""
Unit tests for the Student Grade System logic modules.
Run via: py -m unittest discover tests
"""

import unittest
from logic.calculator import calculate_weighted_average, evaluate_academic_standing
from logic.validators import validate_grade, validate_student_profile, validate_subject_details

class TestLogic(unittest.TestCase):
    
    def test_weighted_average_calculation(self):
        # Case 1: Standard GWA calculation
        # CS101 (3 units): 90.0, CS102 (4 units): 80.0
        # Expected: ((90 * 3) + (80 * 4)) / 7 = 590 / 7 = 84.2857... -> 84.29
        grades = [(90.0, 3.0), (80.0, 4.0)]
        self.assertEqual(calculate_weighted_average(grades), 84.29)
        
        # Case 2: No records logged
        self.assertIsNone(calculate_weighted_average([]))
        
        # Case 3: Zero units error checking
        with self.assertRaises(ValueError):
            calculate_weighted_average([(90.0, 0.0)])
            
        # Case 4: Negative units error checking
        with self.assertRaises(ValueError):
            calculate_weighted_average([(90.0, -1.0)])

    def test_field_validations(self):
        # Valid values check
        try:
            validate_grade(85.0)
            validate_grade("92.5") # parsable string
            validate_student_profile("2026-0001", "Jane", "Doe", "BSCS")
            validate_subject_details("CS101", "Programming", 3.0)
        except ValueError:
            self.fail("Validators raised ValueError unexpectedly on valid inputs.")
            
        # Invalid grade values
        with self.assertRaises(ValueError):
            validate_grade(-1.0)
        with self.assertRaises(ValueError):
            validate_grade(101.0)
        with self.assertRaises(ValueError):
            validate_grade("not_numeric")
            
        # Invalid student profile values
        with self.assertRaises(ValueError):
            validate_student_profile("", "Jane", "Doe", "BSCS")
        with self.assertRaises(ValueError):
            validate_student_profile("2026-0001", "  ", "Doe", "BSCS")
            
        # Invalid subject parameters
        with self.assertRaises(ValueError):
            validate_subject_details("", "Programming", 3.0)
        with self.assertRaises(ValueError):
            validate_subject_details("CS101", "Programming", 0.0)

    def test_evaluation_standing_rules(self):
        # Passed & Dean's Lister (average >= 88.0, no individual subject < 80.0)
        pass_status, dl_status = evaluate_academic_standing(89.0, [90.0, 88.0, 92.0])
        self.assertEqual(pass_status, "Passed")
        self.assertEqual(dl_status, "Dean's Lister")
        
        # Passed but DL Not Eligible (average >= 88.0, but one subject grade < 80.0)
        pass_status, dl_status = evaluate_academic_standing(89.5, [95.0, 78.0, 94.0])
        self.assertEqual(pass_status, "Passed")
        self.assertEqual(dl_status, "Not Eligible")
        
        # Passed but DL Not Eligible (average < 88.0, all subjects >= 80.0)
        pass_status, dl_status = evaluate_academic_standing(85.0, [82.0, 88.0, 85.0])
        self.assertEqual(pass_status, "Passed")
        self.assertEqual(dl_status, "Not Eligible")
        
        # Failed (average < 75.0, all subjects >= 70.0)
        pass_status, dl_status = evaluate_academic_standing(74.0, [75.0, 73.0, 74.0])
        self.assertEqual(pass_status, "Failed")
        self.assertEqual(dl_status, "Not Eligible")
        
        # Failed due to a subject below 70.0 (even if average >= 75.0)
        pass_status, dl_status = evaluate_academic_standing(76.5, [82.0, 68.0, 80.0])
        self.assertEqual(pass_status, "Failed")
        self.assertEqual(dl_status, "Not Eligible")
        
        # Empty inputs defaults
        pass_status, dl_status = evaluate_academic_standing(None, [])
        self.assertEqual(pass_status, "Failed")
        self.assertEqual(dl_status, "Not Eligible")

if __name__ == "__main__":
    unittest.main()
