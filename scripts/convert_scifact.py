import ir_datasets
import json
import os

dataset = ir_datasets.load("beir/scifact")

os.makedirs("data", exist_ok=True)
output_file = "data/scifact_docs.jsonl"

with open(output_file, "w", encoding="utf-8") as f:
    for doc in dataset.docs_iter():
        json.dump({
            "doc_id": doc.doc_id,
            "title": doc.title,
            "text": doc.text
        }, f)
        f.write("\n")

print(f"Selesai simpan {output_file}")
