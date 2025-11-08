import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Loaded environment variables from .env")
    except ImportError:
        print("python-dotenv not installed, skipping .env file")
    
    print("Starting EmoRec backend server...")
    print("API Documentation will be available at:")
    print("  - http://localhost:8000/docs")
    print("  - http://localhost:8000/redoc")
    
    uvicorn.run(
        "backend.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "True").lower() == "true",
        log_level="info"
    )
