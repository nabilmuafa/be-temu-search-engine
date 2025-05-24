from elasticsearch import Elasticsearch, helpers
from app.config import ELASTIC_HOST, ELASTIC_USER, ELASTIC_PASSWORD, ELASTIC_INDEX
from app.services.doc2query_service import Doc2QueryService
from typing import List, Dict, Any
import time

class IndexingService:
    def __init__(self):
        """Initialize indexing service with Elasticsearch and doc2query."""
        try:
            self.es = Elasticsearch(ELASTIC_HOST, basic_auth=(ELASTIC_USER, ELASTIC_PASSWORD))
            self.index = ELASTIC_INDEX
            self.doc2query = Doc2QueryService()
        except Exception as e:
            print(f"Error initializing IndexingService: {str(e)}")
            raise

    def create_index(self, force: bool = False):
        """
        Create the Elasticsearch index with proper mappings.
        
        Args:
            force: If True, delete existing index before creating
        """
        try:
            if force and self.es.indices.exists(index=self.index):
                print(f"Deleting existing index '{self.index}'...")
                self.es.indices.delete(index=self.index)

            if not self.es.indices.exists(index=self.index):
                settings = {
                    "index": {
                        "number_of_shards": 1,
                        "number_of_replicas": 1,
                        "refresh_interval": "1s",
                        "analysis": {
                            "analyzer": {
                                "default": {
                                    "type": "standard",
                                    "stopwords": "_english_"
                                }
                            }
                        }
                    }
                }
                
                mappings = {
                    "properties": {
                        "title": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "plot": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "expanded_text": {
                            "type": "text",
                            "analyzer": "standard"
                        },
                        "tags": {
                            "type": "keyword"
                        }
                    }
                }
                
                self.es.indices.create(
                    index=self.index,
                    settings=settings,
                    mappings=mappings
                )
                print(f"Created index '{self.index}' with mappings and settings")
        except Exception as e:
            print(f"Error creating index: {str(e)}")
            raise

    def index_document(self, doc_id: str, title: str, plot: str, tags: List[str] = None):
        """
        Index a document with expanded text using doc2query.
        
        Args:
            doc_id: Unique identifier for the document
            title: Movie title
            plot: Movie plot
            tags: List of tags/genres
        """
        try:
            # Generate expanded text using doc2query
            expanded_text = self.doc2query.expand_document(title, plot)
            
            # Prepare document
            document = {
                "title": title,
                "plot": plot,
                "expanded_text": expanded_text,
                "tags": tags or []
            }
            
            # Index the document
            self.es.index(
                index=self.index,
                id=doc_id,
                document=document
            )
        except Exception as e:
            print(f"Error indexing document {doc_id}: {str(e)}")
            raise

    def bulk_index(self, documents: List[Dict[str, Any]], batch_size: int = 100):
        """
        Bulk index multiple documents with doc2query expansion.
        
        Args:
            documents: List of document dictionaries with id, title, plot, tags
            batch_size: Number of documents to process in each batch
        """
        start_time = time.time()
        total_docs = len(documents)
        indexed_docs = 0
        errors = []

        try:
            for i in range(0, total_docs, batch_size):
                batch = documents[i:i + batch_size]
                actions = []
                
                for doc in batch:
                    try:
                        # Generate expanded text for each document
                        expanded_text = self.doc2query.expand_document(
                            doc['title'],
                            doc['plot']
                        )
                        
                        # Prepare the indexing action
                        action = {
                            "_index": self.index,
                            "_id": doc['id'],
                            "_source": {
                                "title": doc['title'],
                                "plot": doc['plot'],
                                "expanded_text": expanded_text,
                                "tags": doc.get('tags', [])
                            }
                        }
                        actions.append(action)
                    except Exception as e:
                        errors.append({"doc_id": doc['id'], "error": str(e)})
                
                # Bulk index the batch
                if actions:
                    success, failed = helpers.bulk(
                        self.es,
                        actions,
                        stats_only=True,
                        raise_on_error=False
                    )
                    indexed_docs += success
                    
                    # Progress update
                    elapsed = time.time() - start_time
                    docs_per_sec = indexed_docs / elapsed
                    progress = (indexed_docs / total_docs) * 100
                    print(f"Progress: {progress:.1f}% ({indexed_docs}/{total_docs}) - {docs_per_sec:.1f} docs/sec")

            # Final summary
            print(f"\nIndexing completed:")
            print(f"Successfully indexed: {indexed_docs}/{total_docs} documents")
            if errors:
                print(f"Errors occurred: {len(errors)} documents")
                for error in errors[:5]:  # Show first 5 errors
                    print(f"- Doc {error['doc_id']}: {error['error']}")
                if len(errors) > 5:
                    print(f"... and {len(errors) - 5} more errors")
                    
        except Exception as e:
            print(f"Error during bulk indexing: {str(e)}")
            raise 