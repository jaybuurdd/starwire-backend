import os

from utils.logging import config_logging, logger
from config import get_config
from routes.endpoints import register_endpoints

CONFIG = get_config()
config_logging(CONFIG)
api = register_endpoints() 
logger.info(f"GOATS DAO Server configuration complete, currently running in {os.getenv('APP_MODE')}")
