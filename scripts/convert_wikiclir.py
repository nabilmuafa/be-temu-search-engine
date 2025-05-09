import ir_datasets
import json
import os

dataset = ir_datasets.load("wikiclir/en-simple")
output_path = "data/wikiclir_en_simple.jsonl"
os.makedirs("data", exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    for i, doc in enumerate(dataset.docs_iter()):
        json.dump({
            "doc_id": doc.doc_id,
            "title": doc.title,
            "text": doc.text
        }, f)
        f.write("\n")

print(f"✅ Selesai simpan {output_path}")
