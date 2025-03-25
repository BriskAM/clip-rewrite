from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import clips, pages

def create_app():
    app = FastAPI(title="ClipShare", description="A minimalist online clipboard")
    
    # Mount static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    
    # Include routers
    app.include_router(pages.router)
    app.include_router(clips.router, prefix="/api")
    
    return app 