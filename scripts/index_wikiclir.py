from elasticsearch import Elasticsearch, helpers
import json
import os

es = Elasticsearch("http://localhost:9200", basic_auth=("elastic", os.environ.get("ELASTIC_PASSWORD", "changeme")))
index_name = "wikiclir-en"

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)
    print(f"Index '{index_name}' dibuat.")

actions = []
with open("data/wikiclir_en_simple.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        doc = json.loads(line)
        actions.append({
            "_index": index_name,
            "_id": doc["doc_id"],
            "_source": {
                "title": doc["title"],
                "text": doc["text"]
            }
        })

        if len(actions) >= 1000:
            helpers.bulk(es, actions)
            actions = []

if actions:
    helpers.bulk(es, actions)
    print(f"Indexed final {len(actions)} docs")

print("Indexing selesai.")
