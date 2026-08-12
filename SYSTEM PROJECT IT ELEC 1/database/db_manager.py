"""
Database Manager for SQLite.
Exposes queries and manages transactional states for student profiles, subjects, grades, and evaluations.
"""

import sqlite3
from typing import List, Dict, Any, Tuple, Optional
from logic.calculator import calculate_weighted_average, evaluate_academic_standing

DB_NAME = "grades_system.db"

def get_db_connection(db_path: str = DB_NAME) -> sqlite3.Connection:
    """
    Establishes and returns a database connection.
    Enforces SQLite foreign key constraints.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db(db_path: str = DB_NAME) -> None:
    """
    Initializes the database schema and seeds it with default data if empty.
    """
    with get_db_connection(db_path) as conn:
        # Create STUDENT table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS STUDENT (
            student_id TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            program TEXT NOT NULL
        );
        """)
        
        # Create SUBJECT table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS SUBJECT (
            subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_code TEXT UNIQUE NOT NULL,
            subject_name TEXT NOT NULL,
            units REAL NOT NULL
        );
        """)
        
        # Create GRADE table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS GRADE (
            grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            subject_id INTEGER NOT NULL,
            numerical_grade REAL NOT NULL,
            FOREIGN KEY (student_id) REFERENCES STUDENT(student_id) ON DELETE CASCADE,
            FOREIGN KEY (subject_id) REFERENCES SUBJECT(subject_id) ON DELETE CASCADE,
            UNIQUE (student_id, subject_id),
            CHECK(numerical_grade >= 0.0 AND numerical_grade <= 100.0)
        );
        """)
        
        # Create ACADEMIC_EVALUATION table (One-to-One with Student)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS ACADEMIC_EVALUATION (
            evaluation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            calculated_average REAL NOT NULL,
            pass_fail_status TEXT NOT NULL,
            deans_list_status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES STUDENT(student_id) ON DELETE CASCADE
        );
        """)
        
        conn.commit()
    
    # Seed data if empty
    seed_db(db_path)

def seed_db(db_path: str = DB_NAME) -> None:
    """
    Seeds database with initial students, subjects, and grades if database is empty.
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM STUDENT")
        if cursor.fetchone()[0] > 0:
            return # Already seeded or has data
            
        # Seed Students
        students = [
            ("2026-0001", "Alice", "Smith", "BS Computer Science"),
            ("2026-0002", "Bob", "Johnson", "BS Information Technology"),
            ("2026-0003", "Charlie", "Brown", "BS Software Engineering")
        ]
        conn.executemany("""
        INSERT INTO STUDENT (student_id, first_name, last_name, program)
        VALUES (?, ?, ?, ?)
        """, students)
        
        # Seed Subjects
        subjects = [
            ("CS101", "Introduction to Programming", 3.0),
            ("CS102", "Data Structures & Algorithms", 4.0),
            ("MATH101", "Calculus I", 4.0),
            ("ENG101", "Technical Communication", 3.0)
        ]
        conn.executemany("""
        INSERT INTO SUBJECT (subject_code, subject_name, units)
        VALUES (?, ?, ?)
        """, subjects)
        
        conn.commit()
        
        # Fetch seeded IDs to add grades
        cursor.execute("SELECT subject_id, subject_code FROM SUBJECT")
        subj_map = {row["subject_code"]: row["subject_id"] for row in cursor.fetchall()}
        
        # Seed Grades:
        # Alice (Dean's Lister: Average >= 88.0, no subject < 80)
        alice_grades = [
            ("2026-0001", subj_map["CS101"], 92.5),
            ("2026-0001", subj_map["CS102"], 89.0),
            ("2026-0001", subj_map["MATH101"], 90.0),
            ("2026-0001", subj_map["ENG101"], 88.0)
        ]
        # Bob (Passed, but not Dean's Lister: Average >= 75.0, but has one subject < 80.0)
        bob_grades = [
            ("2026-0002", subj_map["CS101"], 85.0),
            ("2026-0002", subj_map["CS102"], 78.0),
            ("2026-0002", subj_map["MATH101"], 82.0),
            ("2026-0002", subj_map["ENG101"], 75.0)
        ]
        # Charlie (Failed: has a grade below 70)
        charlie_grades = [
            ("2026-0003", subj_map["CS101"], 80.0),
            ("2026-0003", subj_map["CS102"], 68.0), # Below 70
            ("2026-0003", subj_map["MATH101"], 72.0),
            ("2026-0003", subj_map["ENG101"], 74.0)
        ]
        
        all_grades = alice_grades + bob_grades + charlie_grades
        conn.executemany("""
        INSERT INTO GRADE (student_id, subject_id, numerical_grade)
        VALUES (?, ?, ?)
        """, all_grades)
        conn.commit()
        
        # Calculate evaluations for seeded data
        recalculate_and_update_evaluation("2026-0001", conn)
        recalculate_and_update_evaluation("2026-0002", conn)
        recalculate_and_update_evaluation("2026-0003", conn)

# Student CRUD
def add_student(student_id: str, first_name: str, last_name: str, program: str, db_path: str = DB_NAME) -> None:
    with get_db_connection(db_path) as conn:
        conn.execute("""
        INSERT INTO STUDENT (student_id, first_name, last_name, program)
        VALUES (?, ?, ?, ?)
        """, (student_id.strip(), first_name.strip(), last_name.strip(), program.strip()))
        conn.commit()

def get_all_students(db_path: str = DB_NAME) -> List[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cursor = conn.execute("SELECT * FROM STUDENT ORDER BY last_name, first_name")
        return [dict(row) for row in cursor.fetchall()]

def get_student(student_id: str, db_path: str = DB_NAME) -> Optional[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cursor = conn.execute("SELECT * FROM STUDENT WHERE student_id = ?", (student_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def delete_student(student_id: str, db_path: str = DB_NAME) -> None:
    with get_db_connection(db_path) as conn:
        conn.execute("DELETE FROM STUDENT WHERE student_id = ?", (student_id,))
        conn.commit()

# Subject CRUD
def add_subject(subject_code: str, subject_name: str, units: float, db_path: str = DB_NAME) -> None:
    with get_db_connection(db_path) as conn:
        conn.execute("""
        INSERT INTO SUBJECT (subject_code, subject_name, units)
        VALUES (?, ?, ?)
        """, (subject_code.strip().upper(), subject_name.strip(), units))
        conn.commit()

def get_all_subjects(db_path: str = DB_NAME) -> List[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cursor = conn.execute("SELECT * FROM SUBJECT ORDER BY subject_code")
        return [dict(row) for row in cursor.fetchall()]

def get_subject(subject_id: int, db_path: str = DB_NAME) -> Optional[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cursor = conn.execute("SELECT * FROM SUBJECT WHERE subject_id = ?", (subject_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def delete_subject(subject_id: int, db_path: str = DB_NAME) -> None:
    with get_db_connection(db_path) as conn:
        conn.execute("DELETE FROM SUBJECT WHERE subject_id = ?", (subject_id,))
        conn.commit()

# Grade CRUD & Recalculate
def upsert_grade(student_id: str, subject_id: int, numerical_grade: float, db_path: str = DB_NAME) -> None:
    with get_db_connection(db_path) as conn:
        cursor = conn.execute(
            "SELECT grade_id FROM GRADE WHERE student_id = ? AND subject_id = ?",
            (student_id, subject_id)
        )
        row = cursor.fetchone()
        if row:
            conn.execute(
                "UPDATE GRADE SET numerical_grade = ? WHERE student_id = ? AND subject_id = ?",
                (numerical_grade, student_id, subject_id)
            )
        else:
            conn.execute(
                "INSERT INTO GRADE (student_id, subject_id, numerical_grade) VALUES (?, ?, ?)",
                (student_id, subject_id, numerical_grade)
            )
        conn.commit()
        # Recalculate academic evaluation for the student
        recalculate_and_update_evaluation(student_id, conn)

def get_student_grades(student_id: str, db_path: str = DB_NAME) -> List[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cursor = conn.execute("""
        SELECT g.grade_id, g.numerical_grade, s.subject_id, s.subject_code, s.subject_name, s.units
        FROM GRADE g
        JOIN SUBJECT s ON g.subject_id = s.subject_id
        WHERE g.student_id = ?
        ORDER BY s.subject_code
        """, (student_id,))
        return [dict(row) for row in cursor.fetchall()]

def delete_grade(grade_id: int, student_id: str, db_path: str = DB_NAME) -> None:
    with get_db_connection(db_path) as conn:
        conn.execute("DELETE FROM GRADE WHERE grade_id = ?", (grade_id,))
        conn.commit()
        recalculate_and_update_evaluation(student_id, conn)

# Academic Evaluation REC
def recalculate_and_update_evaluation(student_id: str, conn: Optional[sqlite3.Connection] = None, db_path: str = DB_NAME) -> None:
    """
    Recalculates student weighted average and academic evaluation, writing results directly to SQLite.
    """
    is_internal_conn = False
    if conn is None:
        conn = get_db_connection(db_path)
        is_internal_conn = True
        
    try:
        # Get grades and credit units for the student
        cursor = conn.execute("""
        SELECT g.numerical_grade, s.units
        FROM GRADE g
        JOIN SUBJECT s ON g.subject_id = s.subject_id
        WHERE g.student_id = ?
        """, (student_id,))
        rows = cursor.fetchall()
        
        grades_with_units = [(row["numerical_grade"], row["units"]) for row in rows]
        subject_grades = [row["numerical_grade"] for row in rows]
        
        avg = calculate_weighted_average(grades_with_units)
        
        if avg is not None:
            pass_status, dl_status = evaluate_academic_standing(avg, subject_grades)
            
            cursor_check = conn.execute("SELECT evaluation_id FROM ACADEMIC_EVALUATION WHERE student_id = ?", (student_id,))
            row_check = cursor_check.fetchone()
            
            if row_check:
                conn.execute("""
                UPDATE ACADEMIC_EVALUATION
                SET calculated_average = ?, pass_fail_status = ?, deans_list_status = ?
                WHERE student_id = ?
                """, (avg, pass_status, dl_status, student_id))
            else:
                conn.execute("""
                INSERT INTO ACADEMIC_EVALUATION (student_id, calculated_average, pass_fail_status, deans_list_status)
                VALUES (?, ?, ?, ?)
                """, (student_id, avg, pass_status, dl_status))
        else:
            conn.execute("DELETE FROM ACADEMIC_EVALUATION WHERE student_id = ?", (student_id,))
            
        if is_internal_conn:
            conn.commit()
    finally:
        if is_internal_conn and conn:
            conn.close()

def get_student_evaluation(student_id: str, db_path: str = DB_NAME) -> Optional[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cursor = conn.execute("SELECT * FROM ACADEMIC_EVALUATION WHERE student_id = ?", (student_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_all_evaluations(db_path: str = DB_NAME) -> List[Dict[str, Any]]:
    with get_db_connection(db_path) as conn:
        cursor = conn.execute("""
        SELECT 
            s.student_id, s.first_name, s.last_name, s.program,
            e.calculated_average, e.pass_fail_status, e.deans_list_status
        FROM STUDENT s
        LEFT JOIN ACADEMIC_EVALUATION e ON s.student_id = e.student_id
        ORDER BY s.last_name, s.first_name
        """)
        return [dict(row) for row in cursor.fetchall()]
