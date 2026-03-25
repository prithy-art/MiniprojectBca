# ============================================
# models.py
# Database table creation
# Ensures all tables exist on application startup
# ============================================

from database import get_connection


def create_tables():
    """
    Create all required database tables if they don't exist.
    Tables: teachers, students, attendance
    Also inserts a default admin user if not present.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Create teachers table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS teachers (
                teacher_id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            );
        """)

        # Create students table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id SERIAL PRIMARY KEY,
                roll_number VARCHAR(20) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                department VARCHAR(50) NOT NULL,
                year INT NOT NULL,
                email VARCHAR(100)
            );
        """)

        # Create attendance table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                attendance_id SERIAL PRIMARY KEY,
                student_id INT REFERENCES students(student_id) ON DELETE CASCADE,
                date DATE NOT NULL,
                status VARCHAR(10) NOT NULL CHECK (status IN ('Present', 'Absent')),
                UNIQUE(student_id, date)
            );
        """)

        # Create internal marks table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS internal_marks (
                mark_id SERIAL PRIMARY KEY,
                student_id INT REFERENCES students(student_id) ON DELETE CASCADE,
                unit_test_1 INT CHECK (unit_test_1 >= 0 AND unit_test_1 <= 100),
                unit_test_2 INT CHECK (unit_test_2 >= 0 AND unit_test_2 <= 100),
                unit_test_3 INT CHECK (unit_test_3 >= 0 AND unit_test_3 <= 100),
                UNIQUE(student_id)
            );
        """)

        # Insert default admin teacher if not exists
        cur.execute("""
            INSERT INTO teachers (username, password)
            VALUES ('admin', 'admin123')
            ON CONFLICT (username) DO NOTHING;
        """)

        conn.commit()
        print("Database tables created successfully.")

    except Exception as e:
        conn.rollback()
        print(f"Error creating tables: {e}")
        raise e

    finally:
        cur.close()
        conn.close()
