"""
Main application entry point for Render deployment.
This file provides the FastAPI app that Render expects to find.
"""
from src.api.main import app

# Export the app for Render
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
