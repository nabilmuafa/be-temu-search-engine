from elasticsearch import Elasticsearch
from app.config import ELASTIC_HOST, ELASTIC_USER, ELASTIC_PASSWORD, ELASTIC_INDEX

class RetrievalService:
    def __init__(self):
        self.es = Elasticsearch(ELASTIC_HOST, basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD))
        self.index = ELASTIC_INDEX

    def search(self, query: str, top_k: int = 10):
        response = self.es.search(
            index=self.index,
            query={
                "multi_match": {
                    "query": query,
                    "fields": ["title", "text"]
                }
            },
            size=top_k
        )
        return [
            {
                "doc_id": hit["_id"],
                "score": hit["_score"],
                "title": hit["_source"]["title"],
                "text": hit["_source"]["text"][:300],
            }
            for hit in response["hits"]["hits"]
        ]
