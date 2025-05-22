from fastapi import FastAPI
from app.routes import search, llm

app = FastAPI(title="Temu Search API")

app.include_router(search.router)
app.include_router(llm.router, prefix="/llm", tags=["LLM"])
