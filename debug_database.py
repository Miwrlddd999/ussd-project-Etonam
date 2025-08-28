import sqlite3
from database import authenticate_student, get_student_grades
import os

def check_database():
    """Debug script to check database contents and authentication"""
    
    # Check if database file exists
    db_path = 'instance/students.db'
    if not os.path.exists(db_path):
        print(f"❌ Database file not found at: {db_path}")
        return
    
    print(f"✅ Database file exists at: {db_path}")
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"📋 Tables in database: {[table[0] for table in tables]}")
        
        # Check students table
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        print(f"👥 Number of students: {student_count}")
        
        if student_count > 0:
            # Show first few students
            cursor.execute("SELECT index_number, password, name FROM students LIMIT 5")
            students = cursor.fetchall()
            print("\n📝 Sample students:")
            for student in students:
                print(f"  Index: {student[0]}, Password: {student[1]}, Name: {student[2]}")
        
        # Check grades table
        cursor.execute("SELECT COUNT(*) FROM grades")
        grades_count = cursor.fetchone()[0]
        print(f"📊 Number of grade records: {grades_count}")
        
        conn.close()
        
        # Test authentication with sample data
        print("\n🔐 Testing authentication:")
        test_cases = [
            ('0722000040', 'password1'),
            ('0722000012', 'password2'),
            ('0722000030', 'password3')
        ]
        
        for index, password in test_cases:
            result = authenticate_student(index, password)
            if result:
                print(f"  ✅ {index} + {password} = SUCCESS (ID: {result['id']}, Name: {result['name']})")
                
                # Test getting grades
                grades = get_student_grades(result['id'])
                print(f"    📊 Grades found: {len(grades)}")
            else:
                print(f"  ❌ {index} + {password} = FAILED")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    check_database()
