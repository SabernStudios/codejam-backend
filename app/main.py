from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

from app.database import Base, engine, get_db
from app.models import SubmissionDB, ScoreDB, UserDB
from app.schemas import (
    SubmissionCreate,
    SubmissionUpdate,
    SubmissionRead,
    ScoreCreate,
    ScoreRead,
    LeaderboardItem,
    UserCreate,
    UserRead,
    LoginRequest,
    TokenResponse,
)
from app.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    require_judge_or_admin,
    verify_password,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CodeJam Backend API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    existing_submission = (
        db.query(SubmissionDB)
        .filter(SubmissionDB.user_id == current_user.id)
        .first()
    )

    if existing_submission is not None:
        raise HTTPException(
            status_code=400,
            detail="This account already has a submission"
        )

    new_submission = SubmissionDB(
        user_id=current_user.id,
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

@app.get("/submissions/me", response_model=SubmissionRead)
def get_my_submission(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    submission = (
        db.query(SubmissionDB)
        .filter(SubmissionDB.user_id == current_user.id)
        .first()
    )

    if submission is None:
        raise HTTPException(
            status_code=404,
            detail="No submission found for this account"
        )

    return submission

@app.put("/submissions/me", response_model=SubmissionRead)
def update_my_submission(
    submission_data: SubmissionUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    submission = (
        db.query(SubmissionDB)
        .filter(SubmissionDB.user_id == current_user.id)
        .first()
    )

    if submission is None:
        raise HTTPException(
            status_code=404,
            detail="No submission found for this account"
        )

    update_data = submission_data.model_dump(
        exclude_unset=True,
        mode="json"
    )

    for field, value in update_data.items():
        setattr(submission, field, value)

    db.commit()
    db.refresh(submission)

    return submission

@app.put("/submissions/{submission_id}", response_model=SubmissionRead)
def update_submission(
    submission_id: int,
    submission_data: SubmissionUpdate,
    db: Session = Depends(get_db)
):
    submission = (
        db.query(SubmissionDB)
        .filter(SubmissionDB.id == submission_id)
        .first()
    )

    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")

    update_data = submission_data.model_dump(
        exclude_unset=True,
        mode="json"
    )

    for field, value in update_data.items():
        setattr(submission, field, value)

    db.commit()
    db.refresh(submission)

    return submission

@app.post("/scores", response_model=ScoreRead)
def create_score(
    score_data: ScoreCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_judge_or_admin)
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

@app.post("/auth/register", response_model=UserRead)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    if not user_data.username or not user_data.password:
        raise HTTPException(
            status_code=400,
            detail="Username and password are required"
        )

    existing_user = (
        db.query(UserDB)
        .filter(UserDB.username == user_data.username)
        .first()
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )

    new_user = UserDB(
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        role="student"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/auth/login", response_model=TokenResponse)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = (
        db.query(UserDB)
        .filter(UserDB.username == form_data.username)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }

@app.get("/auth/me", response_model=UserRead)
def get_me(current_user: UserDB = Depends(get_current_user)):
    return current_user