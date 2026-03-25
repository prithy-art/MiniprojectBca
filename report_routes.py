# ============================================
# report_routes.py
# Report generation API routes
# Uses Pandas to generate CSV reports
# ============================================

import os
import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from database import get_connection

router = APIRouter()

# Directory to store exported CSV files
EXPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")


@router.get("/report/{date}")
def generate_report(date: str):
    """
    Generate an attendance report for a specific date.
    Returns attendance summary and a downloadable CSV file.
    Date format: YYYY-MM-DD
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Fetch attendance records for the given date
        cur.execute(
            """
            SELECT s.roll_number, s.name, s.department, a.status, a.date
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.date = %s
            ORDER BY s.roll_number
            """,
            (date,)
        )
        rows = cur.fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"No attendance records found for date: {date}"
            )

        # Create a Pandas DataFrame
        df = pd.DataFrame(rows, columns=[
            "Roll Number", "Student Name", "Department", "Status", "Date"
        ])

        # Calculate attendance summary
        total_students = len(df)
        present_count = len(df[df["Status"] == "Present"])
        absent_count = len(df[df["Status"] == "Absent"])

        # Create exports directory if it doesn't exist
        os.makedirs(EXPORTS_DIR, exist_ok=True)

        # Save CSV file
        csv_path = os.path.join(EXPORTS_DIR, "Attendance_Report.csv")
        df.to_csv(csv_path, index=False)

        return {
            "date": date,
            "total_students": total_students,
            "present": present_count,
            "absent": absent_count,
            "records": df.to_dict(orient="records"),
            "csv_file": "Attendance_Report.csv"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")

    finally:
        cur.close()
        conn.close()


@router.get("/report/download/{date}")
def download_report(date: str):
    """
    Download the attendance report CSV for a specific date.
    First generates the report, then returns the CSV file.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Fetch attendance records
        cur.execute(
            """
            SELECT s.roll_number, s.name, s.department, a.status, a.date
            FROM attendance a
            JOIN students s ON a.student_id = s.student_id
            WHERE a.date = %s
            ORDER BY s.roll_number
            """,
            (date,)
        )
        rows = cur.fetchall()

        if not rows:
            raise HTTPException(
                status_code=404,
                detail=f"No attendance records found for date: {date}"
            )

        # Create DataFrame and save to CSV
        df = pd.DataFrame(rows, columns=[
            "Roll Number", "Student Name", "Department", "Status", "Date"
        ])

        os.makedirs(EXPORTS_DIR, exist_ok=True)
        csv_path = os.path.join(EXPORTS_DIR, "Attendance_Report.csv")
        df.to_csv(csv_path, index=False)

        # Return CSV file as download
        return FileResponse(
            path=csv_path,
            filename="Attendance_Report.csv",
            media_type="text/csv"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading report: {str(e)}")

    finally:
        cur.close()
        conn.close()
