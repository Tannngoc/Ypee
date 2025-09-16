from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import yaml, os

# Load config
with open("config/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

db_path = config["database"]["path"]
os.makedirs(os.path.dirname(db_path), exist_ok=True)

engine = create_engine(f"sqlite:///{db_path}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Product Model
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    itemid = Column(String, unique=True, nullable=False)
    shopid = Column(String, nullable=False)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    rating = Column(Float)
    historical_sold = Column(Integer)
    image = Column(String)
    affiliate_link = Column(Text)

def init_db():
    Base.metadata.create_all(engine)
    return SessionLocal
