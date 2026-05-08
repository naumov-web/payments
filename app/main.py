from fastapi import FastAPI

def create_app() -> FastAPI:
    app = FastAPI(
        title="Internal Wallet Service"
    )

    return app


app = create_app()