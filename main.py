import uvicorn
from dotenv import load_dotenv
import os
from app import create_app

# Load environment variables
load_dotenv()

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("RELOAD", "true").lower() == "true"
    ) 