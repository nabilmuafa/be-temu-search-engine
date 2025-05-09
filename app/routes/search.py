from fastapi import APIRouter, Query
from app.services.retrieval_service import RetrievalService

router = APIRouter()
retrieval = RetrievalService()

@router.get("/search")
def search(q: str = Query(...), top_k: int = 10):
    return {"results": retrieval.search(q, top_k)}
