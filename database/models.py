# database/models.py
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .session import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    asin = Column(String, unique=True, index=True, nullable=False)  # Amazon Standard ID
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    image = Column(String)
    price = Column(Float)
    rating = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    videos = relationship("Video", back_populates="product")


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    script = Column(Text, nullable=False)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="videos")
    publish_logs = relationship("PublishLog", back_populates="video")


class PublishLog(Base):
    __tablename__ = "publish_logs"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"), nullable=False)
    platform = Column(String, default="YouTube")
    status = Column(String, default="pending")  # success / failed / pending
    message = Column(Text)
    published_at = Column(DateTime)

    video = relationship("Video", back_populates="publish_logs")
