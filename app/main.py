from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import LikeDB, SubmissionDB, ScoreDB, UserDB
from app.schemas import (
    IpDuplicateReportItem,
    LikeStatus,
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
        "https://oshscodejam.com",
        "https://www.oshscodejam.com",
        "https://codejam-frontend-six.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def ensure_database_schema():
    """Small production-safe schema patch until this project uses Alembic migrations."""
    with engine.begin() as connection:
        if engine.dialect.name == "postgresql":
            connection.execute(text(
                "ALTER TABLE users "
                "ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL"
            ))
            connection.execute(text(
                "ALTER TABLE users "
                "ADD COLUMN IF NOT EXISTS registration_ip VARCHAR"
            ))
            connection.execute(text(
                "ALTER TABLE scores "
                "ADD COLUMN IF NOT EXISTS user_experience INTEGER DEFAULT 1 NOT NULL"
            ))
        elif engine.dialect.name == "sqlite":
            user_columns = [row[1] for row in connection.execute(text("PRAGMA table_info(users)")).fetchall()]
            score_columns = [row[1] for row in connection.execute(text("PRAGMA table_info(scores)")).fetchall()]

            if "created_at" not in user_columns:
                connection.execute(text(
                    "ALTER TABLE users "
                    "ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL"
                ))

            if "registration_ip" not in user_columns:
                connection.execute(text(
                    "ALTER TABLE users "
                    "ADD COLUMN registration_ip VARCHAR"
                ))

            if "user_experience" not in score_columns:
                connection.execute(text(
                    "ALTER TABLE scores "
                    "ADD COLUMN user_experience INTEGER DEFAULT 1 NOT NULL"
                ))


def get_client_ip(request: Request) -> str | None:
    cloudflare_ip = request.headers.get("cf-connecting-ip")
    if cloudflare_ip:
        return cloudflare_ip.strip()

    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()

    if request.client:
        return request.client.host

    return None


def get_like_count(db: Session, submission_id: int) -> int:
    return db.query(LikeDB).filter(LikeDB.submission_id == submission_id).count()


def get_like_eligibility(user: UserDB) -> tuple[bool, str | None, int | None]:
    if user.created_at is None:
        return False, "This account does not have a creation time recorded.", None

    created_at = user.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)

    eligible_at = created_at + timedelta(days=2)
    now = datetime.now(timezone.utc)

    if now < eligible_at:
        seconds_remaining = (eligible_at - now).total_seconds()
        hours_remaining = max(1, int((seconds_remaining + 3599) // 3600))
        return (
            False,
            f"Accounts must be at least 2 days old to like projects. Try again in about {hours_remaining} hour(s).",
            hours_remaining,
        )

    return True, None, 0


def get_submission_or_404(submission_id: int, db: Session) -> SubmissionDB:
    submission = (
        db.query(SubmissionDB)
        .filter(SubmissionDB.id == submission_id)
        .first()
    )

    if submission is None:
        raise HTTPException(status_code=404, detail="Submission not found")

    return submission


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


@app.get("/submissions/{submission_id}", response_model=SubmissionRead)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db)
):
    return get_submission_or_404(submission_id, db)


@app.get("/submissions/{submission_id}/likes", response_model=LikeStatus)
def get_submission_likes(
    submission_id: int,
    db: Session = Depends(get_db)
):
    get_submission_or_404(submission_id, db)

    return LikeStatus(
        submission_id=submission_id,
        likes=get_like_count(db, submission_id),
        liked=False,
        can_like=False,
        reason="Sign in with an account older than 2 days to like this project.",
    )


@app.get("/submissions/{submission_id}/like-status", response_model=LikeStatus)
def get_submission_like_status(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    get_submission_or_404(submission_id, db)

    existing_like = (
        db.query(LikeDB)
        .filter(
            LikeDB.submission_id == submission_id,
            LikeDB.user_id == current_user.id
        )
        .first()
    )

    can_like, reason, hours_until_eligible = get_like_eligibility(current_user)

    return LikeStatus(
        submission_id=submission_id,
        likes=get_like_count(db, submission_id),
        liked=existing_like is not None,
        can_like=can_like,
        reason=reason,
        hours_until_eligible=hours_until_eligible,
    )


@app.post("/submissions/{submission_id}/like", response_model=LikeStatus)
def like_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    get_submission_or_404(submission_id, db)

    can_like, reason, hours_until_eligible = get_like_eligibility(current_user)
    if not can_like:
        raise HTTPException(status_code=403, detail=reason)

    existing_like = (
        db.query(LikeDB)
        .filter(
            LikeDB.submission_id == submission_id,
            LikeDB.user_id == current_user.id
        )
        .first()
    )

    if existing_like is None:
        db.add(LikeDB(submission_id=submission_id, user_id=current_user.id))
        db.commit()

    return LikeStatus(
        submission_id=submission_id,
        likes=get_like_count(db, submission_id),
        liked=True,
        can_like=True,
        reason=None,
        hours_until_eligible=hours_until_eligible,
    )


@app.delete("/submissions/{submission_id}/like", response_model=LikeStatus)
def unlike_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    get_submission_or_404(submission_id, db)

    existing_like = (
        db.query(LikeDB)
        .filter(
            LikeDB.submission_id == submission_id,
            LikeDB.user_id == current_user.id
        )
        .first()
    )

    if existing_like is not None:
        db.delete(existing_like)
        db.commit()

    can_like, reason, hours_until_eligible = get_like_eligibility(current_user)

    return LikeStatus(
        submission_id=submission_id,
        likes=get_like_count(db, submission_id),
        liked=False,
        can_like=can_like,
        reason=reason,
        hours_until_eligible=hours_until_eligible,
    )


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
    submission = get_submission_or_404(submission_id, db)

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
    get_submission_or_404(score_data.submission_id, db)

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
        average_user_experience = sum(score.user_experience for score in scores) / len(scores)

        total_score = (
            average_creativity
            + average_functionality
            + average_technical_effort
            + average_presentation
            + average_user_experience
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
                average_user_experience=round(average_user_experience, 2),
                total_score=round(total_score, 2),
                number_of_scores=len(scores),
            )
        )

    leaderboard.sort(key=lambda item: item.total_score, reverse=True)
    return leaderboard


@app.get("/admin/ip-duplicates", response_model=list[IpDuplicateReportItem])
def get_ip_duplicates(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_judge_or_admin)
):
    users = (
        db.query(UserDB)
        .filter(UserDB.registration_ip.isnot(None))
        .all()
    )

    groups = {}
    for user in users:
        groups.setdefault(user.registration_ip, []).append(user.username)

    report = []
    for registration_ip, usernames in groups.items():
        if len(usernames) > 1:
            report.append(
                IpDuplicateReportItem(
                    registration_ip=registration_ip,
                    account_count=len(usernames),
                    usernames=usernames,
                )
            )

    report.sort(key=lambda item: item.account_count, reverse=True)
    return report


@app.post("/auth/register", response_model=UserRead)
def register_user(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    if not user_data.name or not user_data.username or not user_data.password:
        raise HTTPException(
            status_code=400,
            detail="Name, username, and password are required"
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

    client_ip = get_client_ip(request)
    if client_ip:
        existing_ip_user = (
            db.query(UserDB)
            .filter(UserDB.registration_ip == client_ip)
            .first()
        )

        if existing_ip_user is not None:
            raise HTTPException(
                status_code=400,
                detail="An account has already been registered from this network. If this is a shared school or family network, contact CSHS."
            )

    new_user = UserDB(
        name=user_data.name,
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        role="student",
        registration_ip=client_ip,
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


@app.get("/me", response_model=UserRead)
def get_me(current_user: UserDB = Depends(get_current_user)):
    return current_user
