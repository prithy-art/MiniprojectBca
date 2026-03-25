# ============================================
# main.py
# FastAPI application entry point
# Attendance Marker System Backend
# ============================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import create_tables
from auth import router as auth_router
from student_routes import router as student_router
from attendance_routes import router as attendance_router
from report_routes import router as report_router
from internal_marks_routes import router as internal_marks_router
from performance_routes import router as performance_router

# Create FastAPI application instance
app = FastAPI(
    title="Attendance Marker System",
    description="A web-based attendance management system for college teachers",
    version="1.0.0"
)

# ============================================
# CORS Middleware
# Allow React frontend to communicate with backend
# ============================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://attendance-marking-frontend.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================
# Include API routers
# ============================================
app.include_router(auth_router, tags=["Authentication"])
app.include_router(student_router, tags=["Students"])
app.include_router(attendance_router, tags=["Attendance"])
app.include_router(internal_marks_router, tags=["Internal Marks"])
app.include_router(performance_router, tags=["Performance Tracker"])
app.include_router(report_router, tags=["Reports"])


# ============================================
# Startup Event
# Create database tables on application start
# ============================================
@app.on_event("startup")
def on_startup():
    """Initialize database tables when the server starts."""
    print("Starting Attendance Marker System...")
    create_tables()
    print("Server is ready!")


# ============================================
# Root endpoint
# ============================================
@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "Attendance Marker System API is running"}
