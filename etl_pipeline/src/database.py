import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from loguru import logger
from contextlib import contextmanager
import os

# Get absolute path to config.yaml
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "config.yaml")

# Load configuration
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

DB_CONFIG = config["database"]
DB_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['db_name']}"

# Create engine and session factory
engine = create_engine(DB_URL, pool_size=10, max_overflow=5)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def get_db_session():
    """Provides a database session and ensures cleanup."""
    session = SessionLocal()
    try:
        yield session  # Session is provided here
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Database transaction failed: {e}")
        raise  # Re-raise the exception for debugging
    finally:
        session.close()
