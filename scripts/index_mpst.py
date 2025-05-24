from elasticsearch import Elasticsearch, helpers
import json
import os

# Inisialisasi koneksi Elasticsearch
es = Elasticsearch("http://es:9200",
                   basic_auth=("elastic", os.environ.get(
                       "ELASTIC_PASSWORD", "changeme")),
                   verify_certs=False)

index_name = "movies"

# Cek dan buat index jika belum ada
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body={
        "mappings": {
            "properties": {
                "title": {"type": "text"},
                "plot": {"type": "text"},
                "tags": {"type": "keyword"}
            }
        }
    })
    print(f"Index '{index_name}' dibuat.")

# Persiapkan indexing batch
actions = []
with open("data/mpst_docs.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        doc = json.loads(line)
        actions.append({
            "_index": index_name,
            "_id": doc["doc_id"],
            "_source": {
                "title": doc["title"],
                "plot": doc["plot"],
                "tags": doc["tags"]
            }
        })

        if len(actions) >= 1000:
            helpers.bulk(es, actions)
            print("Indexed 1000 docs...")
            actions = []

# Index sisa dokumen
if actions:
    helpers.bulk(es, actions)
    print(f"Indexed {len(actions)} docs (final batch)")

print("Indexing selesai.")
