from fastapi import FastAPI

from app.search.router import router as search_router


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(search_router)

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app
