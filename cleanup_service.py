import os
import shutil
from datetime import datetime, timezone
from sqlalchemy.orm import sessionmaker
from app.models.database import engine
from app.models.clip import Clip

def cleanup_expired_clips():
    """Remove expired clips from database and their associated files."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Find all expired clips
        expired_clips = db.query(Clip).filter(Clip.expires_at < datetime.now(timezone.utc)).all()
        
        print(f"Found {len(expired_clips)} expired clips to clean up")
        
        for clip in expired_clips:
            # Remove files if they exist
            if clip.file_path and os.path.exists(clip.file_path):
                try:
                    shutil.rmtree(clip.file_path)
                    print(f"Removed files for clip {clip.access_code}")
                except Exception as e:
                    print(f"Error removing files for clip {clip.access_code}: {e}")
            
            # Remove from database
            db.delete(clip)
        
        db.commit()
        print(f"Successfully cleaned up {len(expired_clips)} expired clips")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

def cleanup_orphaned_files():
    """Remove orphaned files that don't have corresponding database entries."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        uploads_dir = "uploads"
        if not os.path.exists(uploads_dir):
            return
        
        # Get all access codes from database
        active_codes = {clip.access_code for clip in db.query(Clip.access_code).all()}
        
        # Check upload directories and individual files
        orphaned_items = []
        for item in os.listdir(uploads_dir):
            if item.startswith('.'):  # Skip hidden files like .DS_Store
                continue
                
            item_path = os.path.join(uploads_dir, item)
            
            if os.path.isdir(item_path):
                # Check if this looks like an access code directory
                if len(item) == 4 and item.isdigit() and item not in active_codes:
                    orphaned_items.append(('directory', item_path))
            else:
                # Check if this is an orphaned individual file
                # Format: {access_code}_{filename} or {access_code}.{ext}
                if '_' in item or '.' in item:
                    potential_code = item.split('_')[0] if '_' in item else item.split('.')[0]
                    if len(potential_code) == 4 and potential_code.isdigit() and potential_code not in active_codes:
                        orphaned_items.append(('file', item_path))
        
        print(f"Found {len(orphaned_items)} orphaned items to clean up")
        
        for item_type, item_path in orphaned_items:
            try:
                if item_type == 'directory':
                    shutil.rmtree(item_path)
                    print(f"Removed orphaned directory: {item_path}")
                else:
                    os.unlink(item_path)
                    print(f"Removed orphaned file: {item_path}")
            except Exception as e:
                print(f"Error removing orphaned {item_type} {item_path}: {e}")
        
    except Exception as e:
        print(f"Error during orphaned file cleanup: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print(f"Starting cleanup at {datetime.now()}")
    cleanup_expired_clips()
    cleanup_orphaned_files()
    print(f"Cleanup completed at {datetime.now()}")
