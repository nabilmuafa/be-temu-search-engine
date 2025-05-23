from fastapi import APIRouter, Query, Depends
from typing import Optional, List
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from pydantic import BaseModel, Field

router = APIRouter()
retrieval = RetrievalService()
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

@router.post("/generate", summary="Generate text using LLM")
async def generate_text(request: GenerateRequest):
    """
    Generate text using the LLM model.
    
    Parameters:
    - prompt: Text prompt to generate from
    - max_length: Maximum length of generated text (1-2048)
    - temperature: Controls randomness (0.1-2.0, lower is more deterministic)
    """
    generated_text = llm_service.generate(
        request.prompt, 
        max_length=request.max_length,
        temperature=request.temperature
    )
    return {"generated_text": generated_text}

@router.post("/enhanced-search", summary="Search with LLM enhancement")
async def enhanced_search(request: SearchRequest):
    """
    Search using Elasticsearch and enhance results with LLM summary.
    
    Parameters:
    - query: Search query text
    - top_k: Number of results to return (1-50)
    - tags: Optional list of tags to filter results
    
    Returns:
    - results: List of search results
    - summary: LLM-generated summary of the top result
    """
    results = retrieval.search(request.query, request.top_k, request.tags)
    
    # Generate summary using LLM
    summary = llm_service.enhance_search_results(request.query, results)
    
    return {
        "results": results,
        "summary": summary
    } 