import os
from typing import Annotated, Optional
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import text
from db import get_db_session
from file_storage import upload_file
from models import JobApplication, JobBoard, JobPost
from config import settings

app = FastAPI()

@app.get("/api/health")
async def health():
  try:
    with get_db_session() as session:
        session.execute(text("SELECT 1"))
        return {"database": "ok"}
  except Exception as e:
    print(e)
    return {"database": "down"}

@app.get("/api/job-boards")
async def api_job_boards():
    with get_db_session() as session:
       jobBoards = session.query(JobBoard).all()
       return jobBoards
    


# from typing import Annotated
# @app.post("/api/job-boards")
# async def api_create_new_job_board(slug: Annotated[str, Form()]):
#    return {"slug": slug}



class JobBoardForm(BaseModel):
   slug : str = Field(..., min_length=3, max_length=20)
   logo: UploadFile = File(...)

# @app.post("/api/job-boards")
# async def api_create_new_job_board(job_board_form: Annotated[JobBoardForm, Form()]):
#    return {"slug": job_board_form.slug, \
#            "file": job_board_form.logo.filename}

@app.post("/api/job-boards")
async def api_create_new_job_board(job_board_form: Annotated[JobBoardForm, Form()]):
   logo_contents = await job_board_form.logo.read()
   file_url = upload_file("company-logos", job_board_form.logo.filename, logo_contents, job_board_form.logo.content_type)
   with get_db_session() as session:
      new_job_board = JobBoard(slug=job_board_form.slug, logo_url=file_url)
      session.add(new_job_board)
      session.commit()
      session.refresh(new_job_board)
      return new_job_board

if not settings.PRODUCTION:
   app.mount("/uploads", StaticFiles(directory="uploads"))

@app.get("/api/job-boards/{job_board_id}/job-posts")
async def api_company_job_board_posts(job_board_id):
  with get_db_session() as session:
     jobPosts = session.query(JobPost).filter(JobPost.job_board_id.__eq__(job_board_id)).all()
     return jobPosts

@app.get("/api/job-boards/{job_board_id}")
async def api_get_company_job_board(job_board_id):
  with get_db_session() as session:
     jobBoard = session.get(JobBoard, job_board_id)
     if not jobBoard:
        raise HTTPException(status_code=404)
     return jobBoard
  
class JobBoardEditForm(BaseModel):
   slug : str = Field(..., min_length=3, max_length=20)
   logo: Optional[UploadFile] = None

@app.put("/api/job-boards/{job_board_id}")
async def api_get_company_job_board(job_board_id, job_board_edit_form: Annotated[JobBoardEditForm, Form()]):
  with get_db_session() as session:
     jobBoard = session.get(JobBoard, job_board_id)
     if not jobBoard:
        raise HTTPException(status_code=404)
     jobBoard.slug = job_board_edit_form.slug
     if job_board_edit_form.logo is not None:
        logo_contents = await job_board_edit_form.logo.read()
        file_url = upload_file("company-logos", job_board_edit_form.logo.filename, logo_contents, job_board_edit_form.logo.content_type)
        jobBoard.logo_url = file_url
     session.add(jobBoard)
     session.commit()
     return jobBoard

@app.post("/api/job-posts/{job_post_id}/close")
async def api_close_job_post(job_post_id):
  with get_db_session() as session:
     jobPost = session.get(JobPost, job_post_id)
     if not jobPost:
        raise HTTPException(status_code=404)
     jobPost.is_open = False
     session.add(jobPost)
     session.commit()
     return jobPost

@app.get("/api/job-boards/{slug}")
async def api_company_job_board(slug):
  with get_db_session() as session:
     jobPosts = session.query(JobPost) \
        .join(JobPost.job_board) \
        .filter(JobBoard.slug.__eq__(slug)) \
        .all()
     return jobPosts
  

class JobApplicationForm(BaseModel):
   first_name : str = Field(..., min_length=3, max_length=20)
   last_name : str = Field(..., min_length=3, max_length=20)
   email : EmailStr
   job_post_id : int
   resume: UploadFile = File(...)

@app.post("/api/job-applications")
async def api_create_new_job_application(job_application_form: Annotated[JobApplicationForm, Form()]):
   with get_db_session() as session:
      jobPost = session.get(JobPost, job_application_form.job_post_id)
      if not jobPost or not jobPost.is_open:
         raise HTTPException(status_code=400)
   resume_contents = await job_application_form.resume.read()
   file_url = upload_file("resumes", job_application_form.resume.filename, resume_contents, job_application_form.resume.content_type)
   with get_db_session() as session:
      new_job_application = JobApplication(
         first_name=job_application_form.first_name, 
         last_name=job_application_form.last_name, 
         email=job_application_form.email, 
         job_post_id = job_application_form.job_post_id,
         resume_url=file_url)
      session.add(new_job_application)
      session.commit()
      session.refresh(new_job_application)
      return new_job_application
  
app.mount("/assets", StaticFiles(directory="frontend/build/client/assets"))

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
  indexFilePath = os.path.join("frontend", "build", "client", "index.html")
  return FileResponse(path=indexFilePath, media_type="text/html")