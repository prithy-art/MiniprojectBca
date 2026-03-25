# ============================================
# attendance_routes.py
# Attendance marking API routes
# ============================================

from fastapi import APIRouter, HTTPException
from schemas import AttendanceSubmit
from database import get_connection

router = APIRouter()


@router.post("/attendance")
def mark_attendance(data: AttendanceSubmit):
    """
    Mark attendance for multiple students on a given date.
    Rules:
    - Student must exist in the database
    - Cannot record attendance twice for same student on same date
    - Status must be 'Present' or 'Absent'
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        success_count = 0
        errors = []

        for record in data.records:
            # Validate status
            if record.status not in ('Present', 'Absent'):
                errors.append(f"Student ID {record.student_id}: Invalid status '{record.status}'")
                continue

            # Check if student exists
            cur.execute("SELECT student_id FROM students WHERE student_id = %s", (record.student_id,))
            if cur.fetchone() is None:
                errors.append(f"Student ID {record.student_id}: Student not found")
                continue

            # Check for duplicate attendance on same date
            cur.execute(
                "SELECT attendance_id FROM attendance WHERE student_id = %s AND date = %s",
                (record.student_id, data.date)
            )
            if cur.fetchone() is not None:
                errors.append(f"Student ID {record.student_id}: Attendance already recorded for {data.date}")
                continue

            # Insert attendance record
            cur.execute(
                """
                INSERT INTO attendance (student_id, date, status)
                VALUES (%s, %s, %s)
                """,
                (record.student_id, data.date, record.status)
            )
            success_count += 1

        conn.commit()

        return {
            "message": f"Attendance marked for {success_count} students",
            "success_count": success_count,
            "errors": errors
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        cur.close()
        conn.close()


@router.get("/attendance/{date}")
def get_attendance(date: str):
    """
    Get attendance records for a specific date.
    Returns list of students with their attendance status.
    Date format: YYYY-MM-DD
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            SELECT s.student_id, s.roll_number, s.name, s.department,
                   a.status, a.date
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.date = %s
            ORDER BY s.roll_number
            """,
            (date,)
        )
        rows = cur.fetchall()

        records = []
        for row in rows:
            records.append({
                "student_id": row[0],
                "roll_number": row[1],
                "name": row[2],
                "department": row[3],
                "status": row[4],
                "date": str(row[5])
            })

        return records

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        cur.close()
        conn.close()
