import sqlite3
import logging

def db_connect():
    """
    Connect to the database and return connection and cursor objects.
    Updated to match user's database setup.
    """
    try:
        conn = sqlite3.connect('instance/students.db')
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        return conn, cursor
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        raise e

def authenticate_student(index_number, password):
    """
    Authenticate student using index number and password.
    Returns student data if authentication successful, None otherwise.
    """
    try:
        conn, cursor = db_connect()
        cursor.execute(
            "SELECT id, name, email FROM students WHERE index_number = ? AND password = ?",
            (index_number, password)
        )
        student = cursor.fetchone()
        conn.close()
        return student
    except Exception as e:
        logging.error(f"Authentication error: {e}")
        return None

def get_student_grades(student_id, course_list=None):
    """
    Get grades for a student, optionally filtered by course list.
    """
    try:
        conn, cursor = db_connect()
        if course_list:
            placeholders = ",".join("?" * len(course_list))
            cursor.execute(
                f"SELECT course_name, grade FROM grades WHERE student_id = ? AND course_name IN ({placeholders})",
                (student_id, *course_list)
            )
        else:
            cursor.execute(
                "SELECT course_name, grade FROM grades WHERE student_id = ?",
                (student_id,)
            )
        grades = cursor.fetchall()
        conn.close()
        return grades
    except Exception as e:
        logging.error(f"Error fetching grades: {e}")
        return []
