from fastapi import FastAPI

from academic_service.api import groups
from academic_service.api import directions
from academic_service.api import branches

from academic_service.core.database import engine
from academic_service.models.base import Base


app = FastAPI(
    title="Academic Service",
    version="1.0"
)


@app.on_event("startup")
async def startup():

    print("Creating academic tables...")

    async with engine.begin() as conn:
        await conn.run_sync(
            Base.metadata.create_all
        )


app.include_router(
    groups.router,
    prefix="/api/v1/groups",
    tags=["Groups"]
)


app.include_router(
    directions.router,
    prefix="/api/v1/directions",
    tags=["Directions"]
)


app.include_router(
    branches.router,
    prefix="/api/v1/branches",
    tags=["Branches"]
)


@app.get("/health")
async def health():
    return {
        "service": "academic-service",
        "status": "ok"
    }