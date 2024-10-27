# game_data_api/server/main.py

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from server.api import upload, query, health, async_upload
from server.db.session import engine
from server.db.base import Base
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
ENV = os.getenv("ENV")
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

@app.middleware("http")
async def enforce_https_redirect(request: Request, call_next):
    # Check if the X-Forwarded-Proto header exists and is set to 'http'
    if ENV != "local" and request.headers.get("x-forwarded-proto") == "http":
        # Redirect to HTTPS
        url = request.url.replace(scheme="https")
        return RedirectResponse(url)
    # Otherwise, process the request as usual
    return await call_next(request)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")

# Set up templates
templates = Jinja2Templates(directory=FRONTEND_DIR)


app.include_router(upload.router, prefix="/api", tags=["Upload"])
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(query.router, prefix="/api", tags=["Query"])
app.include_router(async_upload.router, prefix="/api", tags=["Async Upload"])

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# @app.get("/")
# async def root():
#     return {"message": "Welcome to Game Data API"}

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


from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
async def serve_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/load_data", response_class=HTMLResponse)
async def serve_load_data(request: Request):
    return templates.TemplateResponse("load_data.html", {"request": request})

@app.get("/query_data", response_class=HTMLResponse)
async def serve_query_data(request: Request):
    return templates.TemplateResponse("query_data.html", {"request": request})

@app.get("/track_task", response_class=HTMLResponse)
async def serve_track_request(request: Request):
    return templates.TemplateResponse("track_request.html", {"request": request})
