from elasticsearch import Elasticsearch
from app.config import ELASTIC_HOST, ELASTIC_USER, ELASTIC_PASSWORD, ELASTIC_INDEX

class RetrievalService:
    def __init__(self):
        self.es = Elasticsearch(ELASTIC_HOST, basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD))
        self.index = ELASTIC_INDEX

    def search(self, query: str, top_k: int = 10, tags: list[str] = None):
        must_clause = {
            "multi_match": {
                "query": query,
                "fields": ["title", "plot"]
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
            size=top_k
        )

        return [
            {
                "doc_id": hit["_id"],
                "score": hit["_score"],
                "title": hit["_source"]["title"],
                "plot": hit["_source"]["plot"][:300],
                "tags": hit["_source"]["tags"]
            }
            for hit in response["hits"]["hits"]
        ]
