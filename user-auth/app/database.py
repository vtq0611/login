#app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./database.db"

# Create a SQLAlchemy Engine instance for connecting to the database.
# 
# Parameters:
# - DATABASE_URL: A string containing the database connection URL.
# - connect_args={"check_same_thread": False}: This is required for SQLite when using it with 
#   multithreaded applications (like FastAPI or Flask in development). 
#   By default, SQLite restricts connections to the same thread. Setting `check_same_thread` 
#   to False disables this check, allowing the connection to be used across different threads.

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a SQLAlchemy session factory called `SessionLocal`.
#
# Parameters:
# - bind=engine: Binds the session to the database engine created earlier.
# - autocommit=False: Disables automatic committing of transactions. 
#   You will need to explicitly call `session.commit()` to save changes.
# - autoflush=False: Disables automatic flushing of changes to the database before each query.
#   You will need to manually call `session.flush()` if needed before querying.

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

def get_db():
    """
    Dependency that provides a database session.
    This function can be used in FastAPI routes to get a database session.
    It ensures that the session is properly closed after use.
    """
    db = SessionLocal()
    try:
        yield db #trả về phiên
    finally:
        db.close()