import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DB_SERVER   = os.getenv("DB_SERVER", "localhost")
DB_NAME     = os.getenv("DB_NAME", "forge_agent")
DB_USER     = os.getenv("DB_USER", "forge_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_ENCRYPT  = os.getenv("DB_ENCRYPT", "False")

# Build connection string — works for both local SQL Server and Azure SQL
if DB_ENCRYPT == "True":
    # Azure SQL connection string
    connection_string = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"
        f"?driver=ODBC+Driver+17+for+SQL+Server"
        f"&Encrypt=yes"
        f"&TrustServerCertificate=no"
        f"&Connection+Timeout=30"
    )
else:
    # Local SQL Server connection string
    connection_string = (
        f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}"
        f"?driver=ODBC+Driver+17+for+SQL+Server"
    )

engine = create_engine(
    connection_string,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_timeout=30,
    connect_args={"connect_timeout": 30}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
