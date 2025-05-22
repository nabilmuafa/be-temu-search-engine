from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import List, Dict, Any, Optional
import os
from app.config import LLM_MODEL_ID

class LLMService:
    def __init__(self):
        """Initialize the LLM service by loading the model and tokenizer."""
        print(f"Loading LLM model: {LLM_MODEL_ID}")
        self.tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_ID)
        self.model = AutoModelForCausalLM.from_pretrained(
            LLM_MODEL_ID,
            torch_dtype=torch.float16,  # Use fp16 for efficiency
            device_map="auto"  # Automatically use available GPUs or fallback to CPU
        )
        print("LLM model loaded successfully")
        
    def generate(self, prompt: str, max_length: int = 512, temperature: float = 0.7) -> str:
        """
        Generate text using the loaded LLM.
        
        Args:
            prompt: The input prompt for the model
            max_length: Maximum length of the generated text
            temperature: Controls randomness of output (lower is more deterministic)
            
        Returns:
            The generated text
        """
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # Generate text
        with torch.no_grad():
            generated_ids = self.model.generate(
                inputs.input_ids,
                max_length=max_length,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode the generated ids to text
        generated_text = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        
        # Return only the newly generated text (remove the input prompt)
        return generated_text.replace(prompt, "").strip()
    
    def enhance_search_results(self, query: str, search_results: List[Dict[Any, Any]]) -> str:
        """
        Enhance search results with LLM summary.
        
        Args:
            query: The user's search query
            search_results: List of search results from Elasticsearch
            
        Returns:
            A summary or enhanced explanation of the search results
        """
        # Create a prompt that includes the query and search results
        prompt = f"""
Search Query: {query}

Search Results:
"""
        
        # Add top search results to the prompt
        for i, result in enumerate(search_results[:5]):  # Use top 5 results
            prompt += f"\n{i+1}. {result['title']}\n   {result['plot']}\n"
            
        prompt += "\nPlease provide a brief summary of these search results related to the query:"
        
        # Generate summary using the LLM
        return self.generate(prompt, max_length=1024) 