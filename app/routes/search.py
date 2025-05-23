from fastapi import APIRouter
from typing import Optional, List
from app.services.retrieval_service import RetrievalService
from pydantic import BaseModel, Field

router = APIRouter()
retrieval = RetrievalService()

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query text")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of results to return")
    tags: Optional[List[str]] = Field(default=None, description="Optional list of tags to filter results")

    class Config:
        schema_extra = {
            "example": {
                "query": "romance movies with happy endings",
                "top_k": 10,
                "tags": ["romance", "comedy"]
            }
        }

@router.post("/search", summary="Search movies")
async def search(request: SearchRequest):
    """
    Search for movies using Elasticsearch.
    
    Parameters:
    - query: Search query text
    - top_k: Number of results to return (1-50)
    - tags: Optional list of tags to filter results
    
    Returns:
    - results: List of search results matching the query and filters
    """
    return {
        "results": retrieval.search(
            query=request.query,
            top_k=request.top_k,
            tags=request.tags
        )
    }
