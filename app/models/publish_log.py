from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class PublishLog(Base):
    __tablename__ = "publish_logs"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    platform = Column(String, default="YouTube")
    status = Column(String, default="pending")  # success / failed / pending
    message = Column(Text)
    published_at = Column(DateTime)

    video = relationship("Video", back_populates="publish_logs")
