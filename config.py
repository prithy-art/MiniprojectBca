# ============================================
# config.py
# Database configuration for PostgreSQL
# Reads from environment variables for security
# ============================================

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Primary: Use DATABASE_URL if available (recommended for Render deployment)
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Fallback: Individual connection settings
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "attendance_system")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
