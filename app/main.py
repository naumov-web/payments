from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config.settings import get_settings
from app.infrastructure.database.engine import engine
from app.interfaces.http.routers.health import router as health_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

    await engine.dispose()

def create_app() -> FastAPI:
    settings = get_settings()
    result = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
    )
    result.state.settings = settings
    result.include_router(health_router)

    return result


app = create_app()