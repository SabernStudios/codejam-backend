from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional

app = FastAPI(title="CodeJam Backend API")


class SubmissionCreate(BaseModel):
    team_name: str
    team_members: str
    contact_email: EmailStr
    project_title: str
    description: str
    category: str
    project_url: HttpUrl
    github_url: Optional[HttpUrl] = None
    demo_video_url: Optional[HttpUrl] = None


class Submission(SubmissionCreate):
    id: int


submissions: list[Submission] = []
next_submission_id = 1


@app.get("/")
def root():
    return {
        "message": "CodeJam Backend API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }


@app.post("/submissions")
def create_submission(submission_data: SubmissionCreate):
    global next_submission_id

    new_submission = Submission(
        id=next_submission_id,
        **submission_data.model_dump()
    )

    submissions.append(new_submission)
    next_submission_id += 1

    return new_submission


@app.get("/submissions")
def get_submissions():
    return submissions


@app.get("/submissions/{submission_id}")
def get_submission(submission_id: int):
    for submission in submissions:
        if submission.id == submission_id:
            return submission

    raise HTTPException(status_code=404, detail="Submission not found")