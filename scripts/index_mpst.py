import json
import os
import sys
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.services.indexing_service import IndexingService

def main():
    print("Starting MPST indexing process...")
    
    # Initialize indexing service
    indexer = IndexingService()
    
    # Create fresh index with proper mappings
    print("Creating index with mappings...")
    indexer.create_index(force=True)
    
    # Read and prepare documents
    docs = []
    print("Reading MPST documents...")
    with open("data/mpst_docs.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            docs.append({
                "id": doc["doc_id"],
                "title": doc["title"],
                "plot": doc["plot"],
                "tags": doc["tags"]
            })
    
    # Index documents in batches
    total_docs = len(docs)
    print(f"Found {total_docs} documents. Starting indexing with doc2query expansion...")
    
    batch_size = 100  # Smaller batch size since we're doing doc2query expansion
    indexer.bulk_index(docs, batch_size=batch_size)
    
    print("Indexing completed successfully!")

if __name__ == "__main__":
    main()
