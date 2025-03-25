from datetime import datetime
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.clip import Clip

router = APIRouter(tags=["pages"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/retrieve", response_class=HTMLResponse)
async def retrieve_page(request: Request):
    return templates.TemplateResponse("retrieve.html", {"request": request})

@router.get("/view/{access_code}", response_class=HTMLResponse)
async def view_clip(request: Request, access_code: str, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.access_code == access_code).first()
    
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    
    # Check if clip has expired
    if clip.expires_at < datetime.utcnow():
        db.delete(clip)
        db.commit()
        raise HTTPException(status_code=404, detail="Clip has expired")
    
    return templates.TemplateResponse(
        "view.html", 
        {
            "request": request, 
            "clip": clip,
            "is_file": clip.is_file,
            "content": clip.content,
            "language": clip.language,
            "filename": clip.filename,
            "filenames": clip.filenames,
            "access_code": clip.access_code,
            "expires_at": clip.expires_at,
            "is_image": clip.is_image
        }
    ) 