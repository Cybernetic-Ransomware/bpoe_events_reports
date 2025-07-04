import uuid
from logging import INFO

from decouple import config

config.search_path = "./docker"


DEBUG=False
LOGGER_LEVEL= INFO

if config("DEBUG"):
    DEBUG=config("DEBUG")
    LOGGER_LEVEL=10

DB_HANDLER_URL: str = config("DB_HANDLER_URL")

if config("INTERNAL_DIAGNOSTICS_TOKEN"):
    INTERNAL_DIAGNOSTICS_TOKEN = config("INTERNAL_DIAGNOSTICS_TOKEN")
else:
    INTERNAL_DIAGNOSTICS_TOKEN = str(uuid.uuid4())