# Lab 5: Vector DB

In this lab, we will use a vector store to retrieve recommendations from the resumes

When the user applies we will put the resume in the vector store

Then the user can click a recommend button on the UI and the api will retrieve a recommended resume from the database, even if the person has not applied directly for the job.

There are two parts to the lab -- ingestion and retrieval

We will use **Qdrant** vector DB, mainly because it is easy to set up.

Documentation on Qdrant with Langchain - https://docs.langchain.com/oss/python/integrations/vectorstores/qdrant

We will write pyunit tests as we go along

## Part 1: Ingestion

These are the steps for this part:
1. 