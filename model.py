from sqlalchemy import Column, String, DateTime, Integer, Text, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)
    video_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)

    __table_args__ = (
        Index('idx_published_at', 'published_at'),
    )
