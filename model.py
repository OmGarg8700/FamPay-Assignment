from sqlalchemy import Column, String, DateTime, Integer, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON

Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)
    video_id = Column(String(50), unique=True, nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    published_at = Column(DateTime, nullable=False)

    thumbnail_default = Column(String(500), nullable=True)
    thumbnail_medium = Column(String(500), nullable=True)
    thumbnail_high = Column(String(500), nullable=True)

    extra_data = Column(JSON, nullable=True)

    __table_args__ = (
        Index('idx_published_at', 'published_at'),
    )
