import os
import pyodbc
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Update these values to match your SQL Server instance
SERVER = os.getenv("DB_SERVER", "LAPTOP-T4KOEIRP")
DATABASE = os.getenv("DB_NAME", "forge_agent")
DRIVER = "ODBC Driver 17 for SQL Server"

# Windows Authentication (no username/password needed)
CONNECTION_STRING = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)

SQLALCHEMY_URL = (
    f"mssql+pyodbc:///?odbc_connect={CONNECTION_STRING}"
)

engine = create_engine(SQLALCHEMY_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database connection successful.")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


if __name__ == "__main__":
    test_connection()