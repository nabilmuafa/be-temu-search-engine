# Təmu Search Engine - Back End

## 🚀 Public Access

The application can be publicly accessed at:
[search.aldenluth.fi](http://search.aldenluth.fi)

## Local Deployment

Follow these steps to deploy the application locally on your machine.

### Requirements
* Memory at least 4GB (8GB+ recommended for LLM usage)
* Storage at least 32GB (more depending on dataset and model sizes)
* Docker & Docker Compose (for containerized deployment)
* Python 3.10+ (for local non-Docker development/execution)

### Steps
1. **Set up a Python virtual environment (Recommended for local development):**
   Open your terminal in the project root directory and run:
   ```bash
   python -m venv env
   # On Windows
   .\env\Scripts\activate
   # On macOS/Linux
   source env/bin/activate
   ```
2. **Install Python dependencies (for local development):**
   With your virtual environment activated, install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory by copying `.env.example` (you will need to create `.env.example` first if it doesn't exist, using the template provided below or in project documentation). Populate it with your desired settings. The variables are used for:
    * `ES_PORT`: The port that Elasticsearch runs on locally (e.g., 9200).
    * `ELASTIC_PASSWORD`: The password for the local `elastic` user.
    * `MEM_LIMIT`: The Docker memory limit for the local Elasticsearch container.
    * `STACK_VERSION`: The version of the Elasticsearch Docker image for local deployment.
    * `ELASTIC_INDEX`: The default index name for local Elasticsearch (e.g., "movies").
    * `LLM_MODEL_ID`: The Hugging Face model ID for the LLM used locally.

4. Run:
    ```bash
    docker compose up -d --build
    ```

    This will build and deploy both the FastAPI application and the Elasticsearch image locally.

5. After the local deployment is successful, wait a while as Elasticsearch takes some time to initialize. The FastAPI application might also take some time if downloading a large LLM model on its first startup.
6. The local FastAPI application can be accessed at `http://localhost:8000`. The local Elasticsearch deployment can be accessed at `http://localhost:<ES_PORT>` (e.g., `http://localhost:9200`).

## Indexing (Local Elasticsearch)

This section applies when running the application and Elasticsearch locally.

This search engine is currently configured to use a movie plot dataset (MPST).

1.  **Data Preparation**:
    The `scripts/convert_mpst.py` script is responsible for downloading and preparing the MPST dataset. It will typically save the processed data as a `.jsonl` file in the `data/` directory (which will be created if it doesn't exist).
    ```bash
    python scripts/convert_mpst.py
    ```

2.  **Indexing Data**:
    Once the data is prepared, the `scripts/index_mpst.py` script is used to index this data into your local Elasticsearch deployment. It will use the `ELASTIC_INDEX` name specified in your local `.env` file (e.g., "movies").
    ```bash
    python scripts/index_mpst.py
    ```

## Searching (Local API)

When running locally, searching can be done by accessing the `/search` endpoint on the local FastAPI application with a query parameter `q`. The endpoint also supports parameters for `top_k` results, optional `tags` for filtering, and toggling `rerank` functionality.

For example, to search for 'action movie with a car chase' on your local instance:
```
http://localhost:8000/search?q=action%20movie%20with%20a%20car%20chase
```
A JSON response will be returned containing a list of relevant movie documents, including their scores and original fields (like title and plot). The results can be reranked for better relevance using a neural model.

## LLM Enhanced Summaries

The application also includes an `LLMService` (located in `app/services/llm_service.py`). This service provides a separate capability to generate enhanced summaries for movie search results.

**How it Works:**
This service is designed to take a user's search query and the top movie result (containing its plot and title). It then uses a Language Model to create a concise summary that highlights the movie's key elements and explains its relevance to the original search query.

This design allows for more context-aware explanations of why a search result is relevant, as a distinct step after initial search and retrieval.

