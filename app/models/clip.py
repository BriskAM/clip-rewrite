from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from app.models.database import Base

class Clip(Base):
    __tablename__ = "clips"

    id = Column(Integer, primary_key=True, index=True)
    access_code = Column(String, unique=True, index=True)
    content = Column(Text)
    filename = Column(String, nullable=True)  # For backward compatibility
    filenames = Column(Text, nullable=True)   # Comma-separated list of filenames
    file_path = Column(String, nullable=True)
    language = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_file = Column(Boolean, default=False)
    is_image = Column(Boolean, default=False) 