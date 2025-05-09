from fastapi import FastAPI
from app.routes import search

app = FastAPI(title="Temu Search API")

app.include_router(search.router)
