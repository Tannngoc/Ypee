from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.session import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    asin = Column(String, unique=True, index=True, nullable=False)  # Amazon Standard ID
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    image = Column(String)
    price = Column(Float)
    rating = Column(Float)
    affiliate_tag = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    videos = relationship("Video", back_populates="product")
