from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl

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

class SubmissionUpdate(BaseModel):
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
    technical_effor: int = Field(ge=1, le=10)
    presentation: int = Field(ge=1, le=10)

    comments: Optional[str] = None

class ScoreRead(BaseModel):
    id: int
    submission_id: int
    judge_nam: str

    creativity: int
    functionality: int
    technical_effort: int
    presentation: int

    comments: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class LeaderboardItem(BaseModel):
    submission_id: int
    project_title: str
    team_name: str
    category: str
    average_creativity: float
    average_functionality: float
    average_technical_effort: float
    average_presentation: float
    total_score: float
    number_of_scores: int
