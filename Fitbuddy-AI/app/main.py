from contextlib import asynccontextmanager

from fastapi import FastAPI

from fastapi.staticfiles import StaticFiles

from .config import settings

from .database import create_tables

from .routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create SQLite tables
    create_tables()

    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "FitBuddy - AI Fitness Plan Generator"
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

app.mount(
    "/static",
    StaticFiles(
        directory="static"
    ),
    name="static",
)


# --------------------------------------------------
# ROUTES
# --------------------------------------------------

app.include_router(router)


# --------------------------------------------------
# ROOT API INFORMATION
# --------------------------------------------------

@app.get("/api")
def api_information():

    return {
        "application": "FitBuddy",
        "version": "1.0.0",
        "status": "running",
        "documentation": "/docs",
    }