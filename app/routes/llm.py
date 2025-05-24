from fastapi import APIRouter, Query
from typing import Optional, List
from app.services.retrieval_service import RetrievalService
from app.services.reranker_service import RerankerService
from app.services.llm_service import LLMService
from pydantic import BaseModel, Field

router = APIRouter()
retrieval = RetrievalService()
reranker = RerankerService()
llm_service = LLMService()

class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="The text prompt to generate from")
    max_length: int = Field(default=512, ge=1, le=2048, description="Maximum length of generated text")
    temperature: float = Field(default=0.7, ge=0.1, le=2.0, description="Temperature for text generation")

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

@router.get("/generate", summary="Generate text using LLM")
async def generate_text(
    prompt: str = Query(..., description="The text prompt to generate from"),
    max_length: int = Query(default=512, ge=1, le=2048, description="Maximum length of generated text"),
    temperature: float = Query(default=0.7, ge=0.1, le=2.0, description="Temperature for text generation")
):
    """
    Generate text using the LLM model.
    
    Parameters:
    - prompt: Text prompt to generate from
    - max_length: Maximum length of generated text (1-2048)
    - temperature: Controls randomness (0.1-2.0, lower is more deterministic)
    """
    generated_text = llm_service.generate(
        prompt=prompt, 
        max_length=max_length,
        temperature=temperature
    )
    return {"generated_text": generated_text}

@router.get("/enhanced-search", summary="Search with LLM enhancement and optional reranking")
async def enhanced_search(
    query: str = Query(..., min_length=1, description="Search query text"),
    initial_top_k: int = Query(default=50, ge=1, le=100, description="Number of initial results to fetch before reranking"),
    apply_rerank: bool = Query(default=True, description="Whether to apply reranking to results"),
    final_top_k: int = Query(default=30, ge=1, le=50, description="Number of results to return after potential reranking"),
    tags: Optional[List[str]] = Query(default=None, description="Optional list of tags to filter results")
):
    """
    Search using Elasticsearch, optionally rerank, and enhance results with LLM summary.
    
    Process:
    1. Retrieves initial results using Elasticsearch (BM25) - controlled by `initial_top_k`.
    2. If `apply_rerank` is true, reranks the initial results using a neural cross-encoder model.
    3. Returns the top `final_top_k` results.
    4. Generates an LLM summary based on the (potentially reranked) top result(s).
    
    Parameters:
    - query: Search query text
    - initial_top_k: Number of initial results to fetch (1-100, default 50)
    - apply_rerank: Whether to apply reranking (defaults to True)
    - final_top_k: Number of results to return after reranking (1-50, default 30)
    - tags: Optional list of tags to filter results
    
    Returns:
    - results: List of search results, potentially reranked.
    - summary: LLM-generated summary of the top result(s).
    """
    # Get initial results
    initial_results = retrieval.search(
        query=query,
        top_k=initial_top_k,
        tags=tags
    )
    
    processed_results = initial_results

    # Apply reranking if enabled and results exist
    if apply_rerank and initial_results:
        processed_results = reranker.rerank(
            query=query,
            results=initial_results,
            top_k=final_top_k  # Reranker returns the final desired number of results
        )
    elif initial_results: # If not reranking, but have results, take the top final_top_k
        processed_results = initial_results[:final_top_k]
    else: # No initial results
        processed_results = []

    # Generate summary using LLM based on the processed (reranked or sliced) results
    summary = llm_service.enhance_search_results(query, processed_results)
    
    return {
        "results": processed_results,
        "summary": summary
    } 