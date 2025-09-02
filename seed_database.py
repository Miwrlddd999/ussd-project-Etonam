#!/usr/bin/env python3
"""
Database seeding script to initialize the TTU USSD database with sample data
"""

import os
import sqlite3
from database_schema import create_tables, insert_sample_data

def check_database_exists():
    """Check if database file exists and has data"""
    db_path = 'instance/students.db'
    
    # Create instance directory if it doesn't exist
    os.makedirs('instance', exist_ok=True)
    
    if not os.path.exists(db_path):
        print("❌ Database file doesn't exist. Creating...")
        return False
    
    # Check if database has data
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count > 0:
            print(f"✓ Database exists with {count} students")
            return True
        else:
            print("❌ Database exists but is empty")
            return False
    except sqlite3.OperationalError:
        print("❌ Database exists but tables are missing")
        return False

def seed_database():
    """Initialize database with tables and sample data"""
    print("Creating database tables...")
    create_tables()
    print("✓ Tables created successfully")
    
    print("Inserting sample student data...")
    insert_sample_data()
    print("✓ Sample data inserted successfully")

def verify_seeding():
    """Verify that seeding was successful"""
    try:
        conn = sqlite3.connect('instance/students.db')
        cursor = conn.cursor()
        
        # Check students
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]
        
        # Check grades
        cursor.execute("SELECT COUNT(*) FROM grades")
        grade_count = cursor.fetchone()[0]
        
        # Show sample student
        cursor.execute("SELECT index_number, name FROM students LIMIT 1")
        sample_student = cursor.fetchone()
        
        conn.close()
        
        print(f"\n✓ Database seeded successfully!")
        print(f"  - {student_count} students added")
        print(f"  - {grade_count} grades added")
        print(f"  - Sample student: {sample_student[0]} - {sample_student[1]}")
        
    except Exception as e:
        print(f"❌ Error verifying database: {e}")

if __name__ == "__main__":
    print("TTU USSD Database Seeder")
    print("=" * 30)
    
    if not check_database_exists():
        seed_database()
        verify_seeding()
    else:
        print("Database already exists and has data. Skipping seeding.")
        print("To force re-seed, delete the 'instance/students.db' file first.")
