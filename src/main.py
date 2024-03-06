from fastapi import FastAPI

from src.documents import router as documents_router
from src.logos import router as logos_router
from src.projects import router as projects_router
from src.users import router as auth_router
from src.utils.logger.main import setup_logging

setup_logging()

app = FastAPI()


app.include_router(projects_router.router)
app.include_router(auth_router.router)
app.include_router(documents_router.router)
app.include_router(logos_router.router)


@app.get("/health")
def read_health() -> dict[str, str]:
    return {"status": "It's ALIVE!"}
