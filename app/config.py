import os
from dotenv import load_dotenv

load_dotenv()

# Elasticsearch connection
ELASTIC_HOST = f"http://localhost:{os.getenv('ES_PORT', 9200)}"
ELASTIC_USER = "elastic"
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", "123456")

# Index name default
ELASTIC_INDEX = os.getenv("ELASTIC_INDEX", "scifact")
