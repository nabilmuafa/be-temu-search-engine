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
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Generate text
        with torch.no_grad():
            generated_ids = self.model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
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
        # Check if we have any results
        if not search_results:
            return "No search results found for this query."
            
        # Get only the top result
        top_result = search_results[0]
        
        # Create a focused prompt for movie summary
        prompt = f"""Task: Create a brief, focused summary of how this movie relates to the search query "{query}".

Movie Information:
Title: {top_result['title']}
Plot: {top_result['plot']}

Requirements:
1. Maximum 2-3 sentences
2. Focus only on aspects relevant to "{query}"
3. Be direct and concise
4. Do not mention the search query itself
5. Do not include meta-commentary or analysis
6. Do not repeat these instructions

Summary:"""
        
        # Generate summary with strict parameters
        return self.generate(
            prompt, 
            max_length=256,  # Shorter max length to enforce brevity
            temperature=0.2   # Lower temperature for more focused output
        ) 