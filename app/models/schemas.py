from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class ClipBase(BaseModel):
    content: Optional[str] = None
    language: Optional[str] = None
    filename: Optional[str] = None
    filenames: Optional[str] = None
    
class ClipCreate(ClipBase):
    expiration_hours: int = 24
    
class ClipResponse(ClipBase):
    access_code: str
    created_at: datetime
    expires_at: datetime
    is_file: bool = False
    is_image: bool = False
    
    class Config:
        orm_mode = True
        
class ClipAccess(BaseModel):
    access_code: str 