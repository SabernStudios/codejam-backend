from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import SubmissionDB
from app.schemas import SubmissionCreate, SubmissionRead

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CodeJam Backend API")


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

@app.post("/submissions", response_model=SubmissionRead)
def create_submission(
    submission_data: SubmissionCreate,
    db: Session = Depends(get_db)
):
    new_submission = SubmissionDB(
        **submission_data.model_dump(mode="json")
    )

    db.add(new_submission)
    db.commit()
    db.refresh(new_submission)

    return new_submission

@app.get("/submissions", response_model=list[SubmissionRead])
def get_submissions(db: Session = Depends(get_db)):
    return db.query(SubmissionDB).all()

@app.get("/submissions/{submission_id}", response_model=SubmissionRead)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db)
):
    submission = (
        db.query(SubmissionDB)
        .filter(SubmissionDB.id == submission_id)
        .first()
    )

    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")

    return submission