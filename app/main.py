from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import SubmissionDB, ScoreDB
from app.schemas import (
    SubmissionCreate, 
    SubmissionRead, 
    ScoreCreate, 
    ScoreRead, 
    LeaderboardItem
)

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

@app.post("/scores", response_model=ScoreRead)
def create_score(
    score_data: ScoreCreate,
    db: Session = Depends(get_db)
):
    submission = (
        db.query(SubmissionDB)
        .filter(SubmissionDB.id == score_data.submission_id)
        .first()
    )

    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")

    new_score = ScoreDB(**score_data.model_dump())

    db.add(new_score)
    db.commit()
    db.refresh(new_score)

    return new_score

@app.get("/scores", response_model=list[ScoreRead])
def get_scores(db: Session = Depends(get_db)):
    return db.query(ScoreDB).all()

@app.get("/scores/submission/{submission_id}", response_model=list[ScoreRead])
def get_scores_for_submission(
    submission_id: int,
    db: Session = Depends(get_db)
):
    return (
        db.query(ScoreDB)
        .filter(ScoreDB.submission_id == submission_id)
        .all()
    )

@app.get("/leaderboard", response_model=list[LeaderboardItem])
def get_leaderboard(db: Session = Depends(get_db)):
    submissions = db.query(SubmissionDB).all()
    leaderboard = []

    for submission in submissions:
        scores = (
            db.query(ScoreDB)
            .filter(ScoreDB.submission_id == submission.id)
            .all()
        )

        if len(scores) == 0:
            continue

        average_creativity = sum(score.creativity for score in scores) / len(scores)
        average_functionality = sum(score.functionality for score in scores) / len(scores)
        average_technical_effort = sum(score.technical_effort for score in scores) / len(scores)
        average_presentation = sum(score.presentation for score in scores) / len(scores)

        total_score = (
            average_creativity
            + average_functionality
            + average_technical_effort
            + average_presentation
        )

        leaderboard.append(
            LeaderboardItem(
                submission_id=submission.id,
                project_title=submission.project_title,
                team_name=submission.team_name,
                category=submission.category,
                average_creativity=round(average_creativity, 2),
                average_functionality=round(average_functionality, 2),
                average_technical_effort=round(average_technical_effort, 2),
                average_presentation=round(average_presentation, 2),
                total_score=round(total_score, 2),
                number_of_scores=len(scores),
            )
        )

        leaderboard.sort(key=lambda item: item.total_score, reverse=True)