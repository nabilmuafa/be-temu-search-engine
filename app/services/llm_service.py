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

    def generate(self, prompt: str, max_length: int = 512, temperature: float = 0.7, max_new_tokens: Optional[int] = None) -> str:
        """
        Generate text using the loaded LLM.

        Args:
            prompt: The input prompt for the model
            max_length: Maximum length of the generated text (used if max_new_tokens is None)
            temperature: Controls randomness of output (lower is more deterministic)
            max_new_tokens: Explicitly sets the number of new tokens to generate

        Returns:
            The generated text
        """
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}

        generation_kwargs = {
            "attention_mask": inputs["attention_mask"],
            "temperature": temperature,
            "do_sample": True,
            "pad_token_id": self.tokenizer.eos_token_id
        }

        if max_new_tokens is not None:
            generation_kwargs["max_new_tokens"] = max_new_tokens
        else:
            generation_kwargs["max_length"] = max_length

        # Generate text
        with torch.no_grad():
            generated_ids = self.model.generate(
                inputs["input_ids"],
                **generation_kwargs
            )

        # Decode the generated ids to text
        generated_text = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        
        # Return only the newly generated text (remove the input prompt)
        # Ensure prompt is not part of the generated_text for cases where it might be identical or a substring at the start
        if generated_text.startswith(prompt):
            return generated_text[len(prompt):].strip()
        else:
            return generated_text.strip() # Or handle as an unexpected case if prompt must be a prefix

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
        # Note: The prompt you designed in a previous step is assumed here
        prompt = f"""Task: Based on the movie's plot, create a brief summary that highlights its key elements and also explains how it relates to the search query "{query}".

Movie Information:
Title: {top_result['title']}
Plot: {top_result['plot']}

Requirements:
1. Emphasize details from the plot in the summary.
2. Maximum 2-3 sentences.
3. Clearly explain its relevance to "{query}".
4. Be direct and concise.
5. Do not mention the search query itself at all.
6. Do not include meta-commentary or analysis.
7. Do not repeat these instructions.
8. Do not halucinate. 

Summary:"""

        # Generate summary with a slightly larger token budget to allow sentence completion
        summary = self.generate(
            prompt,
            temperature=0.2,   # Lower temperature for more focused output
            max_new_tokens=180
        )

        # Try to ensure the summary ends with a complete sentence.
        if summary and summary[-1] not in ['.', '!', '?']:
            # Find the last sentence-ending punctuation.
            last_period = summary.rfind('.')
            last_exclamation = summary.rfind('!')
            last_question = summary.rfind('?')

            last_punctuation_pos = max(last_period, last_exclamation, last_question)

            if last_punctuation_pos != -1:
                # Trim to the character after the punctuation and strip any trailing space
                summary = summary[:last_punctuation_pos + 1].strip()
            # If no sentence-ending punctuation is found, leave the summary as is.
            # This handles cases like very short phrases or single long sentences.

        return summary