import os
from dotenv import load_dotenv

load_dotenv()

# Elasticsearch connection
ELASTIC_HOST = f"http://es:{os.getenv('ES_PORT', 9200)}"
ELASTIC_USER = "elastic"
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", "changeme")

# Index name default
ELASTIC_INDEX = os.getenv("ELASTIC_INDEX", "movies")

# LLM settings
LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")
