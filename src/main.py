from fastapi import FastAPI

from src.api.routers import routers
from src.config.conf_logger import setup_logger
from src.config.lifespan import lifespan

logger = setup_logger(__name__, "main")


app = FastAPI(lifespan=lifespan)

for tag, router in routers.items():
    app.include_router(router, prefix="/api", tags=[str(tag)])


@app.get("/")
async def healthcheck():
    logger.info("Called first healthcheck")
    return {"status": "OK"}
