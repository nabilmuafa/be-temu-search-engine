# Təmu Search Engine - Back End

## Deployment

### Requirements
* Memory at least 4GB
* Storage at least 32GB
* Docker & Docker Compose

### Steps
1. Initialize a `.env` file containing the variables and values in `.env.example`. The variables are used for:
    * `ES_PORT`: The port that Elasticsearch runs on. The default port is 9200.
    * `ELASTIC_PASSWORD`: The password for the default `elastic` user to access the search engine API.
    * `MEM_LIMIT`: The Docker memory limit for Elasticsearch in bytes. The minimum is 4GB (`4294967296`).
    * `STACK_VERSION`: The version of the Elasticsearch Docker image. At the time this was committed, the latest version is 9.0.0.
    * `ELASTIC_INDEX`: [TO BE USED] The index name that will be mainly used for the search engine.

2. Run:
    ```
    docker compose up -d --build
    ```
    
    This will build and deploy both the FastAPI deployment and the Elasticsearch image.

3. After the deployment is successful, wait a while as Elasticsearch takes some time to initialize.
4. The FastAPI deployment can be accessed at `localhost:8000`, while the Elasticsearch deployment can be accessed at `localhost:9200`.

## Indexing

_As of now, this backend application uses hardcoded index titles retrieved from `ir_datasets`._

This search engine uses the `wikiclir-en-simple` dataset from `ir_datasets` as the main collection. The file is retrieved by running
```
python convert_wikiclir.py
```
that will download the dataset and store it as a `.jsonl` file under the `data/` directory that will be created. Indexing can be done by running
```
index_wikiclir.py
```
which will create an index using the `wikiclir-en-simple` dataset in bulk by communicating with the local Elasticsearch deployment.

## Searching

Searching can be done by accessing `/search` on the FastAPI deployment with a query parameter `q`. For example, if you want to search for 'sonar cloud':
```
/search?q=sonar cloud
```
A JSON response will be returned with the scores, relevant title, and relevant text.

