# ============================================
# auth.py
# Teacher authentication routes
# ============================================

from fastapi import APIRouter, HTTPException
from schemas import TeacherLogin
from database import get_connection

router = APIRouter()


@router.post("/login")
def login(credentials: TeacherLogin):
    """
    Authenticate a teacher.
    Validates username and password against the teachers table.
    Returns success message on valid login.
    """
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Query the teachers table for matching credentials
        cur.execute(
            "SELECT teacher_id, username FROM teachers WHERE username = %s AND password = %s",
            (credentials.username, credentials.password)
        )
        teacher = cur.fetchone()

        if teacher is None:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        return {
            "message": "Login successful",
            "teacher_id": teacher[0],
            "username": teacher[1]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    finally:
        cur.close()
        conn.close()
