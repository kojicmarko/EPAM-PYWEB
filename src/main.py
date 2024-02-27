from fastapi import FastAPI

from src.auth import router as auth_router
from src.projects import router as projects_router
from src.utils.logger.main import setup_logging

setup_logging()

app = FastAPI()

app.include_router(projects_router.router)
app.include_router(auth_router.router)


@app.get("/health")
def read_health() -> dict[str, str]:
    return {"status": "It's ALIVE!"}
