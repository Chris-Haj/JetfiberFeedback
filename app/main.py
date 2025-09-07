from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .database import connect_to_mongo, close_mongo_connection
from .routes import feedback_router, analysis_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Feedback System API",
    version="1.0.0",
    description="API for managing customer feedback for internet installation teams"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]

)

# Include routers
app.include_router(feedback_router)
app.include_router(analysis_router)

# Event handlers
@app.get("/")
async def health_check():
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
