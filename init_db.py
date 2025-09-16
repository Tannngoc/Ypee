# init_db.py
from database.session import Base, engine
from database import models

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Done!")
