# ============================================
# internal_marks_routes.py
# API endpoints for entering and fetching internal marks
# ============================================

from fastapi import APIRouter, HTTPException
from database import get_connection
from schemas import InternalMarksSubmit

router = APIRouter(prefix="/internal-marks")


@router.get("/")
def get_students_with_marks():
    """
    Fetch all students along with their internal marks (if any).
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT 
                s.student_id, 
                s.roll_number, 
                s.name, 
                s.department, 
                s.year,
                im.unit_test_1,
                im.unit_test_2,
                im.unit_test_3
            FROM students s
            LEFT JOIN internal_marks im ON s.student_id = im.student_id
            ORDER BY s.roll_number ASC
        """)
        records = cur.fetchall()
        
        results = []
        for r in records:
            results.append({
                "student_id": r[0],
                "roll_number": r[1],
                "name": r[2],
                "department": r[3],
                "year": r[4],
                "unit_test_1": r[5] if r[5] is not None else "",
                "unit_test_2": r[6] if r[6] is not None else "",
                "unit_test_3": r[7] if r[7] is not None else ""
            })
            
        return results

    except Exception as e:
        print(f"Error fetching internal marks: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

    finally:
        cur.close()
        conn.close()


@router.post("/")
def submit_internal_marks(data: InternalMarksSubmit):
    """
    Submit or update internal marks for multiple students.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        for record in data.records:
            # Handle empty strings from frontend as None for the DB
            ut1 = record.unit_test_1 if record.unit_test_1 is not None else None
            ut2 = record.unit_test_2 if record.unit_test_2 is not None else None
            ut3 = record.unit_test_3 if record.unit_test_3 is not None else None

            # Upsert logic (Insert or Update if exists)
            cur.execute("""
                INSERT INTO internal_marks (student_id, unit_test_1, unit_test_2, unit_test_3)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (student_id) DO UPDATE SET
                    unit_test_1 = EXCLUDED.unit_test_1,
                    unit_test_2 = EXCLUDED.unit_test_2,
                    unit_test_3 = EXCLUDED.unit_test_3
            """, (record.student_id, ut1, ut2, ut3))

        conn.commit()
        return {"message": "Internal marks saved successfully"}

    except Exception as e:
        conn.rollback()
        print(f"Error saving internal marks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cur.close()
        conn.close()
