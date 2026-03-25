# ============================================
# performance_routes.py
# API endpoints for fetching student performance
# ============================================

from fastapi import APIRouter, HTTPException
from database import get_connection

router = APIRouter(prefix="/performance")

@router.get("/{identifier}")
def get_student_performance(identifier: str):
    """
    Fetch a student's performance data by Student ID or Roll Number.
    Calculates attendance percentage and average marks.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # First, find the student and their internal marks
        cur.execute("""
            SELECT 
                s.student_id, 
                s.name, 
                s.roll_number,
                s.department,
                s.year,
                im.unit_test_1, 
                im.unit_test_2, 
                im.unit_test_3
            FROM students s
            LEFT JOIN internal_marks im ON s.student_id = im.student_id
            WHERE s.student_id::text = %s OR s.roll_number = %s
        """, (identifier, identifier))
        
        student_data = cur.fetchone()

        if not student_data:
            raise HTTPException(status_code=404, detail="Student not found")

        student_id = student_data[0]
        name = student_data[1]
        roll_number = student_data[2]
        department = student_data[3]
        year = student_data[4]
        ut1 = student_data[5]
        ut2 = student_data[6]
        ut3 = student_data[7]

        # Second, get attendance stats
        cur.execute("""
            SELECT status, COUNT(*) 
            FROM attendance 
            WHERE student_id = %s 
            GROUP BY status
        """, (student_id,))
        
        attendance_stats = cur.fetchall()
        
        total_classes = 0
        present_classes = 0
        
        for stat in attendance_stats:
            status = stat[0]
            count = stat[1]
            total_classes += count
            if status == 'Present':
                present_classes += count

        attendance_percentage = 0
        if total_classes > 0:
            attendance_percentage = round((present_classes / total_classes) * 100, 2)

        # Calculate average marks
        marks_list = [m for m in [ut1, ut2, ut3] if m is not None]
        average_marks = 0
        if len(marks_list) > 0:
             average_marks = round(sum(marks_list) / len(marks_list), 2)
             
        # Determine status indicator
        # Good Performance vs Needs Improvement
        # Status logic: Needs Improvement if attendance < 75% or avg marks < 50
        status_indicator = "Good Performance"
        
        if total_classes > 0 and attendance_percentage < 75:
             status_indicator = "Needs Improvement"
        elif len(marks_list) > 0 and average_marks < 50:
             status_indicator = "Needs Improvement"
        elif len(marks_list) == 0 and total_classes == 0:
             status_indicator = "No Data"

        return {
             "student_id": student_id,
             "name": name,
             "roll_number": roll_number,
             "department": department,
             "year": year,
             "attendance_percentage": attendance_percentage,
             "total_classes": total_classes,
             "present_classes": present_classes,
             "unit_test_1": ut1,
             "unit_test_2": ut2,
             "unit_test_3": ut3,
             "average_marks": average_marks,
             "status_indicator": status_indicator
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error fetching performance: {e}")
        raise HTTPException(status_code=500, detail="Database connection error")

    finally:
        cur.close()
        conn.close()
