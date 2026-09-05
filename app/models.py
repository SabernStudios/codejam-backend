from sqlalchemy import Column, Integer, String, Text

from app.database import Base

class SubmissionDB(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String, nullable=False)
    team_members = Column(Text, nullable=False)
    contact_email = Column(String, nullable=False)
    project_title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    project_url = Column(String, nullable=False)
    github_url = Column(String, nullable=True)
    demo_video_url = Column(String, nullable=True)