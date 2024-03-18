from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Clear the environment variables (note: ensure this is really needed as it removes all environment variables)
# os.environ.clear()

# Load the environment variables from the .env file
load_dotenv()

# Define a function to get the environment variable or raise an error if it is not set
def get_env_var(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise ValueError(f"Environment variable {var_name} is not set")
    return value

# Construct the SQLALCHEMY_DATABASE_URL ensuring all components are present and valid
POSTGRES_USER = get_env_var('POSTGRES_USER')
POSTGRES_PASSWORD = get_env_var('POSTGRES_PASSWORD')
POSTGRES_SERVER = get_env_var('POSTGRES_SERVER')
POSTGRES_PORT = get_env_var('POSTGRES_PORT')
POSTGRES_DB = get_env_var('POSTGRES_DB')
try:
    POSTGRES_PORT_INT = int(POSTGRES_PORT)  # Ensure POSTGRES_PORT is an integer
except ValueError:
    raise ValueError(f"Invalid port number: {POSTGRES_PORT}")

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT_INT}/{POSTGRES_DB}"

# Create the SQL Alchemy engine, session, and base class
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database session generator
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
