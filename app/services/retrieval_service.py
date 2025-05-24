from elasticsearch import Elasticsearch
from app.config import ELASTIC_HOST, ELASTIC_USER, ELASTIC_PASSWORD, ELASTIC_INDEX
from typing import List, Dict, Any, Optional

class RetrievalService:
    def __init__(self):
        """Initialize retrieval service with Elasticsearch connection."""
        try:
            self.es = Elasticsearch(ELASTIC_HOST, basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD))
            self.index = ELASTIC_INDEX
            
            # Verify connection and index existence
            if not self.es.ping():
                raise ConnectionError("Could not connect to Elasticsearch")
            if not self.es.indices.exists(index=self.index):
                raise ValueError(f"Index '{self.index}' does not exist")
                
        except Exception as e:
            print(f"Error initializing RetrievalService: {str(e)}")
            raise

    def search(self, query: str, top_k: int = 100, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search for documents using Elasticsearch.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            tags: Optional list of tags to filter results
            
        Returns:
            List of search results
        """
        if not query or not query.strip():
            return []
            
        if top_k < 1:
            top_k = 1
        elif top_k > 1000:
            top_k = 1000

        try:
            must_clause = {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "title": {
                                    "query": query,
                                    "boost": 3.0,
                                    "operator": "and"
                                }
                            }
                        },
                        {
                            "match": {
                                "plot": {
                                    "query": query,
                                    "boost": 1.0
                                }
                            }
                        },
                        {
                            "match": {
                                "expanded_text": {
                                    "query": query,
                                    "boost": 0.5
                                }
                            }
                        }
                    ]
                }
            }

            es_query = {
                "bool": {
                    "must": must_clause
                }
            }

            if tags:
                es_query["bool"]["filter"] = {
                    "terms": {
                        "tags": tags
                    }
                }

            response = self.es.search(
                index=self.index,
                query=es_query,
                size=top_k,
                _source=["title", "plot", "tags"],  # Only fetch needed fields
                track_total_hits=True
            )

            total_hits = response["hits"]["total"]["value"]
            max_score = response["hits"]["max_score"] or 0

            results = []
            for hit in response["hits"]["hits"]:
                # Normalize score to 0-1 range
                normalized_score = hit["_score"] / max_score if max_score > 0 else 0
                
                result = {
                    "doc_id": hit["_id"],
                    "score": normalized_score,
                    "title": hit["_source"]["title"],
                    "plot": hit["_source"]["plot"][:300],  # Truncate plot for preview
                    "tags": hit["_source"]["tags"]
                }
                results.append(result)

            return results

        except Exception as e:
            print(f"Error performing search: {str(e)}")
            return []
