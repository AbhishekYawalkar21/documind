from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
from dotenv import load_dotenv

from app.utils.db import engine, get_db, Base
from app.models.document import User, Document, DocumentChunk, AnalysisResult, QAHistory
from app.schemas.document import HealthResponse
from app.routes.documents import router as documents_router

load_dotenv()

# Enable vector extension before creating tables
with engine.connect() as connection:
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    connection.commit()

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DocuMind API",
    description="AI-powered document intelligence system",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents_router)

@app.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Check if API and database are working"""
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "ok",
        "service": "documind-api",
        "database": db_status
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to DocuMind API",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.post("/test")
async def test_endpoint(data: dict, db: Session = Depends(get_db)):
    """Test endpoint"""
    return {
        "received": data,
        "status": "success"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)