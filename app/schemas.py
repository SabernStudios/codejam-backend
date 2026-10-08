from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class SubmissionCreate(BaseModel):
    participant_type: str = "individual"
    team_name: str
    team_members: str
    contact_email: EmailStr
    project_title: str
    description: str
    category: str
    project_url: HttpUrl
    github_url: Optional[HttpUrl] = None
    demo_video_url: Optional[HttpUrl] = None


class SubmissionUpdate(BaseModel):
    participant_type: Optional[str] = None
    team_name: Optional[str] = None
    team_members: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    project_title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    project_url: Optional[HttpUrl] = None
    github_url: Optional[HttpUrl] = None
    demo_video_url: Optional[HttpUrl] = None


class SubmissionRead(BaseModel):
    id: int
    user_id: int
    participant_type: str = "individual"
    team_name: str
    team_members: str
    contact_email: str
    project_title: str
    description: str
    category: str
    project_url: str
    github_url: Optional[str] = None
    demo_video_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ScoreCreate(BaseModel):
    submission_id: int
    judge_name: str

    creativity: int = Field(ge=1, le=10)
    functionality: int = Field(ge=1, le=10)
    technical_effort: int = Field(ge=1, le=10)
    presentation: int = Field(ge=1, le=10)
    user_experience: int = Field(ge=1, le=30)

    comments: Optional[str] = None


class ScoreRead(BaseModel):
    id: int
    submission_id: int
    judge_name: str

    creativity: int
    functionality: int
    technical_effort: int
    presentation: int
    user_experience: int

    comments: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LeaderboardItem(BaseModel):
    submission_id: int
    project_title: str
    participant_type: str = "individual"
    team_name: str
    team_members: str
    category: str
    average_creativity: float
    average_functionality: float
    average_technical_effort: float
    average_presentation: float
    average_user_experience: float
    total_score: float
    number_of_scores: int


class UserCreate(BaseModel):
    name: str
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    name: str
    username: str
    role: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str


class LikeStatus(BaseModel):
    submission_id: int
    likes: int
    liked: bool = False
    can_like: bool = False
    reason: Optional[str] = None
    hours_until_eligible: Optional[int] = None


class IpDuplicateReportItem(BaseModel):
    registration_ip: str
    account_count: int
    usernames: list[str]
