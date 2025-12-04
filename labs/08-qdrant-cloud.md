# Lab 8: Qdrant Cloud (Homework)

Now, let us configure the application to run on the deployment environment. To do this, we need to sign up for qdrant cloud and configure our application to connect to the cloud version.

Here are the steps for this lab:

1. Sign up for a free account at qdrant - https://qdrant.tech/
1. Start a free cluster - https://qdrant.tech/documentation/cloud/create-cluster/
1. Get the QDRANT_API_KEY and QDRANT_URL for the cluster. Update both in the `.env` file
1. Update `config.py` and add these two settings:

```
    QDRANT_API_KEY: str
    QDRANT_URL: AnyUrl
```
1. Create the collection `resumes` on qdrant cloud. Put this code in a script and run it

```python
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from config import settings

embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=settings.OPENAI_API_KEY)
client = QdrantClient(url=str(settings.QDRANT_URL), api_key=settings.QDRANT_API_KEY)
client.create_collection(collection_name="resumes", vectors_config=VectorParams(size=3072, distance=Distance.COSINE))
client.close()
```

1. Update `get_vector_store` function so that it connects to cloud server in production environment
1. Go to render.com and add these two environment variables to your instance - https://render.com/docs/configure-environment-variables
1. Commit the code, push and do a deploy on render

## Hints

### How do I connect to qdrant cloud in langchain?

<details>
<summary>Answer</summary>

```python
        vector_store = QdrantVectorStore.from_existing_collection(
            embedding=embeddings, 
            collection_name="resumes", 
            url=str(settings.QDRANT_URL), 
            api_key=settings.QDRANT_API_KEY)
```

### How do I update get_vector_store?

<details>
<summary>Answer</summary>

We want to use the cloud vector store in production and the file path in laptop

```python
def get_vector_store():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=settings.OPENAI_API_KEY)
    if settings.PRODUCTION:
        vector_store = QdrantVectorStore.from_existing_collection(
            embedding=embeddings, 
            collection_name="resumes", 
            url=str(settings.QDRANT_URL), 
            api_key=settings.QDRANT_API_KEY)
    else:
        vector_store = QdrantVectorStore.from_existing_collection(
            embedding=embeddings, 
            collection_name="resumes", 
            path="qdrant_store")
    return vector_store
```