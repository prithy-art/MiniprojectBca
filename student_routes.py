# ============================================
# student_routes.py
# Student CRUD API routes
# ============================================

from fastapi import APIRouter, HTTPException, Query
from schemas import StudentCreate
from database import get_connection
from typing import Optional

router = APIRouter()


@router.post("/students")
def add_student(student: StudentCreate):
    """
    Add a new student to the database.
    Roll numbers must be unique.
    All required fields must be provided.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO students (roll_number, name, department, year, email)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING student_id
            """,
            (student.roll_number, student.name, student.department,
             student.year, student.email)
        )
        student_id = cur.fetchone()[0]
        conn.commit()

        return {
            "message": "Student added successfully",
            "student_id": student_id
        }

    except Exception as e:
        conn.rollback()
        # Check for duplicate roll number
        if "duplicate key" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(
                status_code=400,
                detail=f"Student with roll number '{student.roll_number}' already exists"
            )
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        cur.close()
        conn.close()


@router.get("/students")
def get_students(search: Optional[str] = Query(None, description="Search by roll number")):
    """
    Get all students or search by roll number.
    If 'search' query parameter is provided, filters by roll number.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        if search:
            # Search students by roll number (partial match)
            cur.execute(
                """
                SELECT student_id, roll_number, name, department, year, email
                FROM students
                WHERE roll_number ILIKE %s
                ORDER BY roll_number
                """,
                (f"%{search}%",)
            )
        else:
            # Get all students
            cur.execute(
                """
                SELECT student_id, roll_number, name, department, year, email
                FROM students
                ORDER BY roll_number
                """
            )

        rows = cur.fetchall()

        students = []
        for row in rows:
            students.append({
                "student_id": row[0],
                "roll_number": row[1],
                "name": row[2],
                "department": row[3],
                "year": row[4],
                "email": row[5]
            })

        return students

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        cur.close()
        conn.close()


@router.delete("/students/{student_id}")
def delete_student(student_id: int):
    """
    Delete a student by their student_id.
    Also deletes associated attendance records (CASCADE).
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Check if student exists
        cur.execute("SELECT student_id FROM students WHERE student_id = %s", (student_id,))
        if cur.fetchone() is None:
            raise HTTPException(status_code=404, detail="Student not found")

        # Delete the student (attendance records cascade-deleted)
        cur.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
        conn.commit()

        return {"message": "Student deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        cur.close()
        conn.close()
