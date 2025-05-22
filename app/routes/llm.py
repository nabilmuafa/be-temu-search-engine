from fastapi import APIRouter, Query, Depends
from typing import Optional
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
from pydantic import BaseModel

router = APIRouter()
retrieval = RetrievalService()
llm_service = LLMService()

class GenerateRequest(BaseModel):
    prompt: str
    max_length: int = 512
    temperature: float = 0.7

@router.post("/generate")
def generate_text(request: GenerateRequest):
    """Generate text using the LLM model."""
    generated_text = llm_service.generate(
        request.prompt, 
        max_length=request.max_length,
        temperature=request.temperature
    )
    return {"generated_text": generated_text}

@router.get("/enhanced-search")
def enhanced_search(q: str = Query(...), top_k: int = 10, tags: Optional[str] = Query(None)):
    """
    Search using Elasticsearch and enhance results with LLM summary.
    
    Returns both the original search results and an LLM-generated summary.
    """
    tags_list = [t.strip() for t in tags.split(",")] if tags else None
    results = retrieval.search(q, top_k, tags_list)
    
    # Generate summary using LLM
    summary = llm_service.enhance_search_results(q, results)
    
    return {
        "results": results,
        "summary": summary
    } 