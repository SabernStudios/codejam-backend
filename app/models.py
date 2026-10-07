from sqlalchemy import Column, ForeignKey, Integer, String, Text

from app.database import Base

class SubmissionDB(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True
    )
    
    team_name = Column(String, nullable=False)
    team_members = Column(Text, nullable=False)
    contact_email = Column(String, nullable=False)
    project_title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    project_url = Column(String, nullable=False)
    github_url = Column(String, nullable=True)
    demo_video_url = Column(String, nullable=True)

class ScoreDB(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    judge_name = Column(String, nullable=False)

    creativity = Column(Integer, nullable=False)
    functionality = Column(Integer, nullable=False)
    technical_effort = Column(Integer, nullable=False)
    presentation = Column(Integer, nullable=False)

    comments = Column(Text, nullable=True)

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="student")
