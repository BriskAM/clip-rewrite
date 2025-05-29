import os
import random
import string
import mimetypes
import zipfile
import io
from datetime import datetime, timedelta
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.clip import Clip
from app.models.schemas import ClipCreate, ClipResponse, ClipAccess

router = APIRouter(tags=["clips"])

# Initialize mimetypes
mimetypes.init()

# Define image file extensions
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']

# Define language extension mapping
LANGUAGE_EXTENSIONS = {
    '.js': 'javascript',
    '.py': 'python',
    '.java': 'java',
    '.cs': 'csharp',
    '.cpp': 'cpp',
    '.c': 'cpp',
    '.html': 'html',
    '.css': 'css',
    '.json': 'json',
    '.xml': 'xml',
    '.md': 'markdown',
    '.sql': 'sql',
    '.sh': 'bash',
    '.txt': 'plaintext',
}

# Generate a random 4-digit access code
def generate_access_code():
    return ''.join(random.choices(string.digits, k=4))

# Detect language from filename
def detect_language(filename):
    ext = os.path.splitext(filename.lower())[1]
    return LANGUAGE_EXTENSIONS.get(ext, '')

@router.post("/clips", response_model=ClipResponse)
async def create_clip(
    content: str = Form(None),
    language: str = Form(None),
    expiration_hours: int = Form(24),
    files: List[UploadFile] = File([]),  # Changed default to empty list
    db: Session = Depends(get_db)
):
    # Create a new clip
    new_clip = Clip(
        access_code=generate_access_code(),
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(hours=expiration_hours),
    )
    
    # Add content if provided
    if content and content.strip():
        new_clip.content = content
        new_clip.language = language
    
    # Handle file uploads if provided
    if files and len(files) > 0:
        # Ensure uploads directory exists
        os.makedirs("uploads", exist_ok=True)
        
        # Create a directory for this clip
        clip_dir = f"uploads/{new_clip.access_code}"
        os.makedirs(clip_dir, exist_ok=True)
        
        # Track if we have images
        has_images = False
        filenames = []
        
        # Save each file
        for file in files:
            if file and file.filename:
                try:
                    # Clean filename to prevent directory traversal
                    safe_filename = "".join(c for c in file.filename if c.isalnum() or c in "._- ")
                    
                    # Save the file
                    file_path = f"{clip_dir}/{safe_filename}"
                    file_content = await file.read()
                    
                    with open(file_path, "wb") as f:
                        f.write(file_content)
                    
                    filenames.append(safe_filename)
                    
                    # Check if file is an image based on extension
                    file_ext = os.path.splitext(safe_filename.lower())[1]
                    if file_ext in IMAGE_EXTENSIONS:
                        has_images = True
                    elif not new_clip.language and file_ext in LANGUAGE_EXTENSIONS:
                        # Auto-detect language for the first code file
                        new_clip.language = LANGUAGE_EXTENSIONS[file_ext]
                    
                    # Reset file cursor for potential reuse
                    await file.seek(0)
                    
                except Exception as e:
                    # If there's an error saving a file, clean up and raise the error
                    if os.path.exists(clip_dir):
                        import shutil
                        shutil.rmtree(clip_dir)
                    raise HTTPException(status_code=500, detail=f"Error saving file {safe_filename}: {str(e)}")
        
        # Set the appropriate fields
        new_clip.filenames = ",".join(filenames)
        new_clip.file_path = clip_dir
        new_clip.is_file = True
        new_clip.is_image = has_images and len(filenames) == 1  # Only set is_image if single image
    
    # Validate that either content or file was provided
    if not new_clip.content and not new_clip.is_file:
        raise HTTPException(status_code=400, detail="Either content or file must be provided")
    
    # Check for duplicate access code
    while db.query(Clip).filter(Clip.access_code == new_clip.access_code).first():
        new_clip.access_code = generate_access_code()
    
    try:
        db.add(new_clip)
        db.commit()
        db.refresh(new_clip)
        return new_clip
    except Exception as e:
        # If there's an error saving to database, clean up uploaded files
        if new_clip.file_path and os.path.exists(new_clip.file_path):
            import shutil
            shutil.rmtree(new_clip.file_path)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating clip: {str(e)}")

@router.get("/clips/{access_code}", response_model=ClipResponse)
def get_clip(access_code: str, db: Session = Depends(get_db)):
    clip = db.query(Clip).filter(Clip.access_code == access_code).first()
    
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    
    # Check if clip has expired
    if clip.expires_at < datetime.utcnow():
        # Clean up files if they exist
        if clip.file_path and os.path.exists(clip.file_path):
            import shutil
            try:
                shutil.rmtree(clip.file_path)
            except Exception:
                pass  # Continue even if file cleanup fails
        
        db.delete(clip)
        db.commit()
        raise HTTPException(status_code=404, detail="Clip has expired")
    
    return clip

@router.get("/clips/{access_code}/download")
def download_clip_file(
    access_code: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    filename: str = None, 
    download_all: bool = False,
    as_text: bool = False
):
    clip = db.query(Clip).filter(Clip.access_code == access_code).first()
    
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")
    
    # Check if clip has expired
    if clip.expires_at < datetime.utcnow():
        db.delete(clip)
        db.commit()
        raise HTTPException(status_code=404, detail="Clip has expired")
    
    # If the clip is just text content, allow downloading as file
    if as_text and clip.content:
        # Create a temporary file with the content
        content_type = "text/plain"
        extension = ".txt"
        
        # Use language to determine file extension
        if clip.language:
            for ext, lang in LANGUAGE_EXTENSIONS.items():
                if lang == clip.language:
                    extension = ext
                    break
        
        temp_filename = f"clip_{access_code}{extension}"
        temp_path = f"uploads/{temp_filename}"
        
        os.makedirs("uploads", exist_ok=True)
        with open(temp_path, "w") as f:
            f.write(clip.content)
        
        response = FileResponse(
            path=temp_path,
            filename=temp_filename,
            media_type=content_type
        )
        
        # Add cleanup task
        background_tasks.add_task(os.unlink, temp_path)
        
        return response
    
    # If user wants to download a specific file
    if clip.is_file and not download_all and filename:
        # Get list of valid filenames
        valid_filenames = [f.strip() for f in clip.filenames.split(",") if f.strip()]
        
        # Check if requested filename is valid
        if filename not in valid_filenames:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = f"{clip.file_path}/{filename}"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Set appropriate media type for images
        media_type = None
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            media_type = mime_type
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=media_type or "application/octet-stream"
        )
    
    # If clip has multiple files and user wants to download all
    if clip.is_file and download_all:
        # Create a zip file containing all files
        zip_filename = f"clip_{access_code}_files.zip"
        temp_zip_path = f"uploads/{zip_filename}"
        
        try:
            os.makedirs("uploads", exist_ok=True)
            
            # Create zip file
            with zipfile.ZipFile(temp_zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
                # Get list of files in the directory
                filenames = [f.strip() for f in clip.filenames.split(",") if f.strip()]
                for filename in filenames:
                    file_path = f"{clip.file_path}/{filename}"
                    if os.path.exists(file_path):
                        zip_file.write(file_path, arcname=filename)
            
            # Add cleanup task
            background_tasks.add_task(os.unlink, temp_zip_path)
            
            return FileResponse(
                path=temp_zip_path,
                filename=zip_filename,
                media_type="application/zip"
            )
            
        except Exception as e:
            if os.path.exists(temp_zip_path):
                os.unlink(temp_zip_path)
            raise HTTPException(status_code=500, detail=f"Error creating zip file: {str(e)}")
    
    # Default: Single file download for backward compatibility
    if clip.is_file and clip.filenames:
        # Get the first valid filename
        filenames = [f.strip() for f in clip.filenames.split(",") if f.strip()]
        if not filenames:
            raise HTTPException(status_code=404, detail="No files found")
            
        filename = filenames[0]
        file_path = f"{clip.file_path}/{filename}"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Set appropriate media type
        media_type = None
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            media_type = mime_type
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type=media_type or "application/octet-stream"
        )
    
    raise HTTPException(status_code=404, detail="No downloadable content found")