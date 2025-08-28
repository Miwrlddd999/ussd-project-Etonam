import sqlite3

# Connect to SQLite database (creates the file if it doesn't exist)
def db_connect():
   conn = sqlite3.connect('instance/students.db')
   conn.row_factory = sqlite3.Row  # Enable access to columns by name
   return conn, conn.cursor()

# Create the students table
def create_tables():
    conn, cursor = db_connect()

    # Students table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            index_number VARCHAR(20) UNIQUE,
            password VARCHAR(100),
            email VARCHAR(100),
            name VARCHAR(100),
            phone VARCHAR(15)
        )
    ''')

    # Grades table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_name VARCHAR(200),
            grade CHAR(2),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()


# Insert sample data
def insert_sample_data():
    conn, cursor = db_connect()

    # List of all courses
    courses = [
        # Level 100 First Semester
        "Communication Skills",
        "Information Technology I",
        "Introduction to Programming Using C++",
        "Discrete Mathematics",
        "Entrepreneurship",
        "Computer Applications",
        "Introduce to Economics",

        # Level 100 Second Semester
        "African Studies",
        "Communication Skills II Industrial Attachment",
        "Programming Using Java",
        "Information Technology II",
        "Database Concepts & Technology",
        "Mathematics & Statistics",
        "Introduction to Economics II",

        # Level 200 First Semester
        "Visual Basic Dot Net",
        "Database Management System (Oracle)",
        "Web Technology I",
        "Hardware Technology I",
        "Networking I",
        "Introduction to Accounting",
        "Research Methodology",

        # Level 200 Second Semester
        "Industrial Attachment II",
        "Hardware Technology II",
        "Introduction to Software Engineering",
        "Web Technology II",
        "Networking II",
        "Entrepreneurship II",
        "Introduction to Accounting II",
        "PHP Programming",

        # Level 300 First Semester
        "Management Information Systems",
        "Systems Analysis and Design",
        "Information Systems Security",
        "Systems Administration I",
        "Operating Systems",

        # Level 300 Second Semester
        "E-Commerce",
        "Systems Administration II",
        "Computer Graphics",
        "Information Systems Security II",
        "Project",
        "Computer Organization & Architecture"
    ]

    # Sample students
    students = [
        ('0722000040', 'password1', '0722000040@ttu.edu.gh', 'Mensah Miguel Etornam Kwame', '0593256158'),
        ('0722000012', 'password2', '0722000012@ttu.edu.gh', 'ANGBATAAYELE VITUS', '0507935569'),
        ('0722000030', 'password3', '0722000030@ttu.edu.gh', 'TORDZRO BLAISE CODJOE', '0553541815'),
        ('0722000047', 'password4', '0722000047@ttu.edu.gh', 'Bless Agambila', '0599180942'),
        ('0722000019', 'password5', '0722000019@ttu.edu.gh', 'Ebenezer Okai Mensah', '0557461295'),
    ]

    # Insert students and grades
    for student in students:
        cursor.execute('''
            INSERT OR IGNORE INTO students (index_number, password, email, name, phone)
            VALUES (?, ?, ?, ?, ?)
        ''', student)
        student_id = cursor.lastrowid

        # Assign grades for all courses (randomized for demo)
        import random
        for course in courses:
            grade = random.choice(['A', 'B', 'C'])
            cursor.execute('''
                INSERT INTO grades (student_id, course_name, grade)
                VALUES (?, ?, ?)
            ''', (student_id, course, grade))

    conn.commit()
    conn.close()

    

create_tables()
insert_sample_data()
