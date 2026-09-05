from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, HttpUrl


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