from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from apiroutes import router
import uvicorn

# Create FastAPI application
app = FastAPI()

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    print(" Database tables created successfully")
except Exception as e:
    print(f" Error creating database tables: {e}")

# Include API routes
app.include_router(router, prefix="/api", tags=["Face Recognition"])

if __name__ == "__main__":
    print("Starting")

    
