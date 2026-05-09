from fastapi import FastAPI
from app.config.settings import get_settings
from app.interfaces.http.routers.health import router as health_router

def create_app() -> FastAPI:
    settings = get_settings()
    result = FastAPI(
        title=settings.app_name,
    )
    result.state.settings = settings
    result.include_router(health_router)

    return result


app = create_app()