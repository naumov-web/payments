from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config.settings import get_settings
from app.infrastructure.database.engine import engine
from app.interfaces.http.routers.health import router as health_router
from app.interfaces.http.routers.actors import router as actors_router
from app.interfaces.http.routers.transfers import router as transfers_router
from app.interfaces.http.routers.purchases import router as purchases_router
from app.interfaces.http.routers.withdrawals import router as withdrawals_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    await engine.dispose()

def create_app() -> FastAPI:
    settings = get_settings()
    result = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
        description=(
            "Internal corporate wallet service "
            "with event sourcing architecture."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=[
            {
                "name": "actors",
                "description": "Actor management endpoints.",
            },
        ]
    )
    result.state.settings = settings
    result.include_router(health_router)
    result.include_router(actors_router)
    result.include_router(transfers_router)
    result.include_router(purchases_router)
    result.include_router(withdrawals_router)

    return result


app = create_app()