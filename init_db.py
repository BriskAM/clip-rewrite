from app.models.database import Base, engine
from app.models.clip import Clip

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!") 