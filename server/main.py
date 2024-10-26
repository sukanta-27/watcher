# game_data_api/server/main.py

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from server.api import upload, query, health
from server.db.session import engine
from server.db.base import Base
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI server
app = FastAPI(
    title="Game Data API",
    description="API for game data management and analytics",
    debug=True,
    version="1.0.0"
)

# Add the following lines
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(query.router, prefix="/api", tags=["Query"])

# Create all tables in the database
Base.metadata.create_all(bind=engine)

@app.get("/")
async def root():
    return {"message": "Welcome to Game Data API"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_422_UNPROCESSABLE_ENTITY]:
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.detail
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )