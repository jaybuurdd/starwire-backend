import os
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

class Config:
    # TODO: Caching config will go here
    CACHE=""

class DevelopmentConfig(Config):
    DEBUG = True
    # DBMaria config
    DB_URL = f"mysql+mysqlconnector://{os.getenv('DB_USERNAME')}:{quote(os.getenv('DB_PASSWORD'))}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    
class ProductionConfig(Config):
    DEBUG = False
    DB_URL = f"mysql+mysqlconnector://{os.getenv('DB_USERNAME')}:{quote(os.getenv('DB_PASSWORD'))}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

def get_config():
    env = os.getenv("APP_MODE", "DEVELOPMENT").upper()
    if env == "DEVELOPMENT":
        return DevelopmentConfig
    elif env == "PRODUCTION":
        return ProductionConfig
    else:
        raise ValueError(f"{env} is not a valid environemnt for this app. Use 'DEVELOPMENT' or 'PRODUCTION'")