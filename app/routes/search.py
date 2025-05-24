from fastapi import APIRouter, Query
from typing import Optional, List
from app.services.retrieval_service import RetrievalService
from app.services.reranker_service import RerankerService
from pydantic import BaseModel, Field

router = APIRouter()
retrieval = RetrievalService()
reranker = RerankerService()


@router.get("/search", summary="Search movies with reranking")
async def search(
    query: str = Query(..., min_length=1, description="Search query text"),
    top_k: int = Query(default=25, ge=1, le=100,
                       description="Number of initial results to fetch"),
    tags: Optional[List[str]] = Query(
        default=None, description="Optional list of tags to filter results"),
    rerank: bool = Query(
        default=True, description="Whether to apply reranking to results"),
    rerank_top_k: int = Query(
        default=25, ge=1, le=100, description="Number of results to return after reranking")
):
    """
    Search for movies using Elasticsearch with neural reranking.

    The search process:
    1. Retrieves initial results using Elasticsearch (BM25) - default 100 results
    2. Reranks all results using a neural cross-encoder model
    3. Returns all reranked results by default, sorted by relevance

    Parameters:
    - query: Search query text
    - top_k: Number of initial results to fetch (1-100, default 100)
    - tags: Optional list of tags to filter results
    - rerank: Whether to apply reranking (defaults to True)
    - rerank_top_k: Number of results to return after reranking (1-100, default 100)

    Returns:
    - results: List of search results, reranked by default for better relevance
    """
    # Get initial results
    results = retrieval.search(
        query=query,
        top_k=top_k,
        tags=tags
    )

    # Apply reranking if enabled (default is True)
    if rerank and results:
        results = reranker.rerank(
            query=query,
            results=results,
            top_k=rerank_top_k
        )

    return {"results": results}
