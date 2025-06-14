from elasticsearch import Elasticsearch, helpers
import json
import os

es = Elasticsearch("http://localhost:9200", basic_auth=("elastic", os.environ.get("ELASTIC_PASSWORD", "changeme")), verify_certs=False)

index_name = "scifact"

# Buat index jika belum ada
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name)
    print(f"Index '{index_name}' dibuat.")

actions = []
with open("data/scifact_docs.jsonl", "r", encoding="utf-8") as f:
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
            print(f"Indexed 1000 docs...")
            actions = []

if actions:
    helpers.bulk(es, actions)
    print(f"Indexed {len(actions)} docs (final batch)")

print("Indexing selesai.")
