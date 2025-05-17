from fastapi import APIRouter, Query
from typing import Optional
from app.services.retrieval_service import RetrievalService

router = APIRouter()
retrieval = RetrievalService()

@router.get("/search")
def search(q: str = Query(...), top_k: int = 10, tags: Optional[str] = Query(None)):
    tags_list = [t.strip() for t in tags.split(",")] if tags else None
    return {"results": retrieval.search(q, top_k, tags_list)}
