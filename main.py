from fastapi import FastAPI, Query
from elasticsearch import Elasticsearch
import os

app = FastAPI()

# Koneksi ke Elasticsearch
es = Elasticsearch("http://es:9200", basic_auth=("elastic", os.environ.get("ELASTIC_PASSWORD", "123456")), verify_certs=False)

@app.get("/search")
def search(q: str = Query(..., description="Search query"), top_k: int = 10):
    response = es.search(
        index="scifact",
        query={
            "multi_match": {
                "query": q,
                "fields": ["title", "text"]
            }
        },
        size=top_k
    )

    results = [
        {
            "doc_id": hit["_id"],
            "score": hit["_score"],
            "title": hit["_source"]["title"],
            "text": hit["_source"]["text"][:300]  # dipotong biar ringkas
        }
        for hit in response["hits"]["hits"]
    ]
    return {"results": results}
