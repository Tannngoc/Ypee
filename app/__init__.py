from config import config
from app.database.session import SessionLocal

CONFIG = config

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
