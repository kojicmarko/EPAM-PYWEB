from fastapi import FastAPI

from src.projects import router as projects_router

app = FastAPI()

app.include_router(projects_router.router)


@app.get("/health")
def read_health() -> dict[str, str]:
    return {"status": "It's ALIVE!"}
