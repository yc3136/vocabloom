import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .secrets import get_secret
from urllib.parse import quote_plus

load_dotenv()

# Get database configuration from environment variables and secrets
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = get_secret("database-password", os.getenv("DB_PASSWORD", "password"))
DB_NAME = os.getenv("DB_NAME", "vocabloom")
DB_HOST = os.getenv("DB_HOST", "localhost")

# URL-encode the password to handle special characters
ENCODED_PASSWORD = quote_plus(DB_PASSWORD)

# Construct DATABASE_URL securely
if os.getenv("ENVIRONMENT") == "production":
    # Production: Use Cloud SQL Auth Proxy
    DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{ENCODED_PASSWORD}@/{DB_NAME}?host={DB_HOST}"
else:
    # Local development
    DATABASE_URL = f"postgresql://{DB_USER}:{ENCODED_PASSWORD}@{DB_HOST}/{DB_NAME}"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,    # Recycle connections after 5 minutes
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 