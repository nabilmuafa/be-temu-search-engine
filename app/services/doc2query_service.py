from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
from typing import List
import numpy as np

class Doc2QueryService:
    def __init__(self):
        """Initialize the doc2query service with a T5 model."""
        print("Loading docT5query model...")
        self.model_name = "castorini/doc2query-t5-base-msmarco"
        try:
            self.tokenizer = T5Tokenizer.from_pretrained(self.model_name)
            self.model = T5ForConditionalGeneration.from_pretrained(
                self.model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            print("docT5query model loaded successfully")
        except Exception as e:
            print(f"Error loading docT5query model: {str(e)}")
            raise

    def generate_queries(self, document: str, num_queries: int = 5) -> List[str]:
        """
        Generate potential search queries for a document.
        
        Args:
            document: The document text to generate queries for
            num_queries: Number of queries to generate
            
        Returns:
            List of generated query strings
        """
        if not document or not document.strip():
            return []
            
        if num_queries < 1:
            num_queries = 1
        elif num_queries > 10:
            num_queries = 10

        try:
            # Add task prefix for T5
            input_text = f"generate query: {document}"
            
            # Prepare input
            input_ids = self.tokenizer.encode(
                input_text,
                max_length=512,
                truncation=True,
                return_tensors="pt"
            ).to(self.model.device)

            # Generate multiple queries
            outputs = self.model.generate(
                input_ids,
                max_length=64,
                do_sample=True,
                top_k=10,
                temperature=0.7,
                num_return_sequences=num_queries,
                num_beams=num_queries,
                no_repeat_ngram_size=2  # Prevent repetitive phrases
            )

            # Decode and return queries
            queries = [
                self.tokenizer.decode(output, skip_special_tokens=True)
                for output in outputs
            ]
            
            # Remove empty queries and duplicates
            queries = [q.strip() for q in queries if q.strip()]
            queries = list(dict.fromkeys(queries))
            
            return queries
        except Exception as e:
            print(f"Error generating queries: {str(e)}")
            return []

    def expand_document(self, title: str, plot: str, num_queries: int = 5) -> str:
        """
        Expand document representation with generated queries.
        
        Args:
            title: Movie title
            plot: Movie plot
            num_queries: Number of queries to generate
            
        Returns:
            Expanded document text
        """
        if not title or not plot:
            return ""
            
        try:
            # Combine title and plot for query generation
            doc_text = f"{title}. {plot}"
            
            # Generate potential queries
            queries = self.generate_queries(doc_text, num_queries)
            
            if not queries:
                return doc_text
            
            # Combine original text with generated queries
            expanded_text = f"{doc_text}\n\nPotential queries: {' | '.join(queries)}"
            
            return expanded_text
        except Exception as e:
            print(f"Error expanding document: {str(e)}")
            return f"{title}. {plot}"  # Return original text on error 