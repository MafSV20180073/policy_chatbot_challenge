from fastapi import FastAPI

from .routes import router

app = FastAPI(title="Mock Order API")

app.include_router(router)
