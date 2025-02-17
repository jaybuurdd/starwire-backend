from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.logging import logger
from config import get_config


db = None
class DatabaseConfig:
    def __init__(self, db_url, debug):
        logger.info("Starting SQL Alchemy configuration...")
        self.engine = create_engine(
            db_url, 
            echo=debug,
            pool_pre_ping=True,
            pool_recycle=1800 # Recycle every 30 min
            )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Test connection
        try:
            with self.engine.connect() as connection:
                logger.info(f"Ending SQL Alchemy configuration: {connection}")
                pass
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise

# Initialize the DatabaseConfig instance globally
config = get_config()
db_config = DatabaseConfig(config.DB_URL, config.DEBUG)

def get_db():
    db = db_config.SessionLocal()
    try:
        yield db
    finally:
        db.close()
