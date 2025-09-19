import os
import yaml
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f) or {}

class Config:
    DB_URL = os.getenv("DATABASE_URL", "sqlite:///./database/Ypee.db")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    VIDEO_API_KEY = os.getenv("PIXVERSE_API_KEY")
    SETTINGS = config