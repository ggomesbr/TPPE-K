from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..config import settings

# Database URL from environment settings
SQLALCHEMY_DATABASE_URL = settings.database_url

# Create SQLAlchemy engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug  # Log SQL queries in debug mode
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import Base after creating engine to avoid circular imports
from ..model.models import Base


def get_database():
    """Dependency to get database session"""
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


# For backwards compatibility with Amis Service pattern
def get_db():
    """Alternative name for database dependency"""
    return get_database()


def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)