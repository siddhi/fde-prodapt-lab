# Lab 6: Retrieve Recommended Resume

In this lab, we will add an API endpoint to retrieve the recommended resume and return it.

Here are the steps to complete:

1. Create a function `get_recommendation` in `ai.py` that takes the job description
1. Create an api endpoint `api_recommend_resume` in `main.py`
    - Path `/api/job-posts/{job_post_id}/recommend`
    - Takes `job_post_id` as a parameter
    - Calls the `get_recommendation` function created in previous step
    - Returns the matching job application

Write tests along with the code.

## High Level Overview

1. We want to implement `get_recommendatation` in `ai.py`. First think about how we will test this function.
1. One way can be to add some resumes to the vector store, then call `get_recommendation` with a job description and see whether it is returning the right one
1. Write a test to do the above. It will fail when you run the tests, since we have not implemented it yet
1. Make the test pass by implementing the functionality in `get_recommendation`
1. Next we need to implement the API. Again -- how will we test this?
1. Maybe we can create a dummy job post with a job description and then upload some resumes. Then we can call the recommendation API using the test client and see if we get the correct output.
1. Write this a pyunit test that does this.
1. Then implement the api endpoint till it passes
1. We are done!

## Hints

### How do I test get_recommendatation?

<details>
<summary>Answer</summary>

```python
def test_retrieval(vector_store):
    for id, filename in enumerate(os.listdir("test/resumes")):
        with open(f"test/resumes/{filename}", "rb") as f:
            content = f.read()
        ingest_resume_for_recommendataions(content, filename, resume_id=id, vector_store=vector_store)
    result = get_recommendation("I am looking for an expert in AI", vector_store)
    assert "Andrew" in result.page_content
```
</details>

### How do I implement get_recommendation?

<details>
<summary>Answer</summary>

```python
def get_recommendation(job_description, vector_store):
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})
    results = retriever.invoke(job_description)
    return results[0]
```
</details>

### How do I test the new API endpoint?

<details>
<summary>Answer</summary>

```python
def test_recommendation_api(db_session, client):
    job_board = JobBoard(slug="test", logo_url="http://example.com")
    db_session.add(job_board)
    db_session.commit()
    db_session.refresh(job_board)
    job_post = JobPost(title="AI Engineer", 
                       description="I am looking for a generalist who can work in python and typescript", 
                       job_board_id = job_board.id)
    db_session.add(job_post)
    db_session.commit()
    db_session.refresh(job_post)
    test_resumes = [
        ('Andrew', 'Ng', 'andrewng@gmail.com', 'ProfileAndrewNg.pdf'),
        ('Koudai', 'Aono', 'koxudaxi@gmail.com', 'ProfileKoudaiAono.pdf')
    ]
    for first_name, last_name, email, filename in test_resumes:
        post_data = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "job_post_id": job_post.id
        }
        with open(f"test/resumes/{filename}", "rb") as f:
            response = client.post("/api/job-applications", data=post_data, files={"resume": (filename, f, "application/pdf")})
    response = client.get(f"/api/job-posts/{job_post.id}/recommend")
    assert response.status_code == 200
    data = response.json()
    assert data['first_name'] == 'Koudai'
    assert data['last_name'] == 'Aono'
```
</details>

### How do I implement the new API endpoint?

<details>
<summary>Answer</summary>

```python
@app.get("/api/job-posts/{job_post_id}/recommend")
async def api_recommend_resume(
   job_post_id, 
   db: Session = Depends(get_db),
   vector_store = Depends(get_vector_store)):
   
   job_post = db.get(JobPost, job_post_id)
   if not job_post:
      raise HTTPException(status_code=400)
   job_description = job_post.description
   recommended_resume = get_recommendation(job_description, vector_store)   
   application_id = recommended_resume.metadata["_id"]
   job_application = db.get(JobApplication, application_id)
   return job_application
```
</details>
