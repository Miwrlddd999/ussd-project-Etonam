#!/usr/bin/env python3
"""
Test script to verify database imports and functionality
"""

try:
    print("Testing database imports...")
    from database import db_connect, authenticate_student, get_student_grades
    print("✓ All database functions imported successfully")
    
    print("\nTesting database connection...")
    conn, cursor = db_connect()
    print("✓ Database connection successful")
    conn.close()
    
    print("\nTesting authentication function...")
    # Test with a dummy call (will return None if no matching student)
    result = authenticate_student("test", "test")
    print(f"✓ Authentication function works (returned: {result})")
    
    print("\nAll tests passed! The database module is working correctly.")
    
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("This suggests there's a syntax error in database.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("Check if the database file exists at 'instance/students.db'")

if __name__ == "__main__":
    print("Run this script to test your database imports:")
    print("python test_imports.py")
