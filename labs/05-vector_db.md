# Lab 5: Vector DB

In this lab, we will use a vector store to retrieve recommendations from the resumes

When the user applies we will put the resume in the vector store

Then the user can click a recommend button on the UI and the api will retrieve a recommended resume from the database, even if the person has not applied directly for the job.

There are two parts to the lab -- ingestion and retrieval. This lab we will do ingestion. Next lab is retrieval.

We will use **Qdrant** vector DB, mainly because it is easy to set up.

Documentation on Qdrant with Langchain - https://docs.langchain.com/oss/python/integrations/vectorstores/qdrant

## Setup pre-work

Update `requirements.txt`:

```
langchain-qdrant==1.1.0 # Langchain with Qdrant vector DB
pypdf==6.4.0 # PDF to Text
```

Then install dependencies

Mac:
```
> source ./.venv/bin/activate
> pip uninstall PyPDF2
> pip install -r requirements.txt
```

Windows:
```
> .\.venv\Scripts\activate
> pip uninstall PyPDF2
> pip install -r requirements.txt
```

Update `converter.py` as follows

```python
from pypdf import PdfReader
```

Now, let us create a Qdrant DB.

Put this code in a script and run it

```python
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from config import settings

embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=settings.OPENAI_API_KEY)
client = QdrantClient(path="qdrant_store")
client.create_collection(collection_name="resumes", vectors_config=VectorParams(size=3072, distance=Distance.COSINE))
client.close()
```

This will create a folder `qdrant_store` which will have our vector db files.

Now lets implement the feature. We will write pyunit tests as we go along.

## High Level Approach

1. Create a new test file `test/test_recommendations`
1. Get the test resumes and put them in `test/resumes`
1. Use this command to run the tests: `pytest .\test\test_recommendation.py` (use whichever slash as per your OS)
1. In `ai.py` create the below function. This will create a Qdrant vector store

```python
def get_vector_store():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=settings.OPENAI_API_KEY)
    vector_store = QdrantVectorStore.from_existing_collection(embedding=embeddings, collection_name="resumes", path="qdrant_store")
    return vector_store
```
1. But while testing, we would like to use an **in memory** vector store and not this one (Why?). So in `ai.py` create a unction `def inmemory_vector_store()` which will conigure qdrant and langchain with an in memory store and yield it. Close the client after yielding, else you will get errors
1. In `conftest.py`, create a pytest fixture `vector_store` which will return the in memory store from `ai.py` (use syntax `yield from inmemory_vector_store()`)
1. Write a test `test_should_embed_text_and_add_to_vector_db`. The test uses the above fixture

```python
def test_should_embed_text_and_add_to_vector_db(vector_store):
    ingest_resume("Siddharta\nSiddharta is an AI trainer", "siddharta.pdf", 1, vector_store)
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})
    result = retriever.invoke("I am looking for an AI trainer")
    assert len(result) == 1
    assert "Siddharta" in result[0].page_content
    assert result[0].metadata['_id'] == 1
```

1. Create a function `ingest_resume` in `ai.py` and make this test pass. Put filename in the metadata field `url` and set the `id` field to what is passed in. Parameters are:
  - resume text (string)
  - filename
  - resume id
  - vector store object

1. Now we need to create the background task that will do this operation. Write this test

```python
def test_background_task(vector_store):
    filename = "test/resumes/ProfileAndrewNg.pdf"
    with open(filename, "rb") as f:
        content = f.read()
    ingest_resume_for_recommendataions(content, filename, resume_id=1, vector_store=vector_store)
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})
    result = retriever.invoke("I am looking for an AI trainer")
    assert "Andrew" in result[0].page_content
```

1. Create the function `ingest_resume_for_recommendation` in `main.py` and make the test pass. It should use the `ingest_resume` function we created above. Parameters are
  - resume content (PDF format bytes, NOT string)
  - filename
  - resume id
  - vector store

1. Now let us test the ingestion functionality. Write a test `def test_retrieval_quality(vector_store)`
  - It should ingest all the resumes in `test/resumes` by calling the background task above
  - Then retrieve the following text and verify the right resume is returned
  - "I am looking for an expert in AI" --> Andrew
  - "I am looking for an expert in Linux" --> Linus
  - "I am looking for an expert in Javascript" --> Yuxi
  - "I am looking for a generalist who can work in python and typescript" --> Koudai
  - "I am looking for a data journalist" --> Simon

1. Now we are going to test the API. This is the code for it. It is a little complex, so read it carefully

```python
def test_job_application_api(db_session, vector_store, client):
    job_board = JobBoard(slug="test", logo_url="http://example.com")
    db_session.add(job_board)
    db_session.commit()
    db_session.refresh(job_board)
    job_post = JobPost(title="AI Engineer", 
                       description="Need an AI Engineer", 
                       job_board_id = job_board.id)
    db_session.add(job_post)
    db_session.commit()
    db_session.refresh(job_post)
    filename = "test/resumes/ProfileAndrewNg.pdf"
    post_data = {
        "first_name": "Siddharta",
        "last_name": "Govindaraj",
        "email": "siddharta@gmail.com",
        "job_post_id": job_post.id
    }
    with open(filename, "rb") as f:
        response = client.post("/api/job-applications", data=post_data, files={"resume": ("ProfileAndrewNg.pdf", f, "application/pdf")})
    assert response.status_code == 200
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})
    result = retriever.invoke("I am looking for an expert in AI")
    assert "Andrew" in result[0].page_content
    assert result[0].metadata["_id"] == job_post.id
```

1. Before the test above can pass, we need to do a few things. Make all the required changes and make the test pass
  - In `main.py`, find the relevant api endpoint and schedule the background task that we created before
  - The background task needs vector store as a parameter. Add it as a dependency to the endpoint function (refer how db has been configured). It should be configured with the *real* vector store
  - In the test case, we want to use the in memory vector store, so we will need to override the real vector store with the in memory one. Again, refer how we are replacing the real db session with the testcontainer one

## Hints

### How can I create the in memory vector store?

<details>
<summary>Answer</summary>

```python
def inmemory_vector_store():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=settings.OPENAI_API_KEY)
    client = QdrantClient(":memory:")
    client.create_collection(collection_name="resumes", vectors_config=VectorParams(size=3072, distance=Distance.COSINE))
    vector_store = QdrantVectorStore(client=client, collection_name="resumes", embedding=embeddings)
    try:
        yield vector_store
    finally:
        client.close()
```
</details>

### How do I create the vector store fixture

<details>
<summary>Answer</summary>

```python
@pytest.fixture(scope="function")
def vector_store():
    yield from inmemory_vector_store()
```
</details>

### What should I do in ingest_resume?

<details>
<summary>Hint</summary>

Create a langchain `Document` object with the given parameters and use `add_documents` function on the store to add it. Set a field `url` in the metadata

Note that we are adding a single document, but `add_documents` requires a list. Pass a list of one document.
`add_documents` also takes a list of `ids`
</details>

<details>
<summary>Answer</summary>

```python
def ingest_resume(resume_text, resume_url, resume_id, vector_store):
    doc = Document(page_content=resume_text, metadata={"url": resume_url})
    vector_store.add_documents(documents=[doc], ids=[resume_id])
```
</details>

### How do I create the background task?

<details>
<summary>Hint</summary>

Use the function `extract_text_from_pdf_bytes` in `converter.py`. Then use `ingest_resume` above
</details>

<details>
<summary>Answer</summary>

```python
def ingest_resume_for_recommendataions(resume_content, resume_url, resume_id, vector_store):
   resume_raw_text = extract_text_from_pdf_bytes(resume_content)
   ingest_resume(resume_raw_text, resume_url, resume_id, vector_store)
```
</details>

### How do I test retrieval quality?

<details>
<summary>Answer</summary>

```python
def test_retrieval_quality(vector_store):
    for id, filename in enumerate(os.listdir("test/resumes")):
        with open(f"test/resumes/{filename}", "rb") as f:
            content = f.read()
        ingest_resume_for_recommendataions(content, filename, resume_id=id, vector_store=vector_store)
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})

    result = retriever.invoke("I am looking for an expert in AI")
    assert "Andrew" in result[0].page_content
    result = retriever.invoke("I am looking for an expert in Linux")
    assert "Linus" in result[0].page_content
    result = retriever.invoke("I am looking for an expert in Javascript")
    assert "Yuxi" in result[0].page_content
    result = retriever.invoke("I am looking for a generalist who can work in python and typescript")
    assert "Koudai" in result[0].page_content
    result = retriever.invoke("I am looking for a data journalist")
    assert "Simon" in result[0].page_content
```
</details>

### How do I specify vector store as a dependency?

<details>
<summary>Answer</summary>

Update the parameters for `api_create_new_job_application` like this

```python
async def api_create_new_job_application(
   job_application_form: Annotated[JobApplicationForm, Form()], 
   background_tasks: BackgroundTasks, 
   db: Session = Depends(get_db),
   vector_store = Depends(get_vector_store)):
```
</details>

### How do I schedule the background task?

<details>
<summary>Answer</summary>

```python
   background_tasks.add_task(ingest_resume_for_recommendataions, resume_content, 
                              file_url, new_job_application.id, vector_store)
```
</details>

### How do I override the real vector store with the in memory one during the api test?

<details>
<summary>Answer</summary>

Update the `client` fixture in `conftest.py`

```python
@pytest.fixture(scope="function")
def client(db_session, vector_store):
    def override_get_db():
        yield db_session

    def override_vector_store():
        yield vector_store
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_vector_store] = override_vector_store
    
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
```
</details>

## Discussion Questions

1. How do we improve performance in vector database?
