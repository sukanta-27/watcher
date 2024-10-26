from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import date

# Upload API Request Model
class UploadRequest(BaseModel):
    file_url: HttpUrl

    class Config:
        json_schema_extra = {
            "example": {
                "file_url": "https://example.com/data.csv"
            }
        }

# Upload API Response Models
class UploadResponse(BaseModel):
    message: str
    rows_processed_successfully: Optional[int] = None
    rows_could_not_be_processed: Optional[int] = None
    errors: Optional[Dict[str, str]] = None
    status: str = "success"

class UploadErrorResponse(BaseModel):
    detail: str

class UploadProcessingErrorResponse(BaseModel):
    message: str
    rows_processed_successfully: Optional[int] = None
    rows_could_not_be_processed: Optional[int] = None
    errors: Optional[Dict[Any, Any]]
    status: str



class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)

class FilterParams(BaseModel):
    # Text fields
    name: Optional[str] = None
    about_the_game: Optional[str] = None
    developers: Optional[List[str]] = None
    publishers: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    genres: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    supported_languages: Optional[List[str]] = None

    # Date fields
    release_date: Optional[date] = None

    # Exact Match Numerical fields
    app_id: Optional[int] = None
    price: Optional[float] = None
    dlc_count: Optional[int] = None
    score_rank: Optional[int] = None
    positive_reviews: Optional[int] = None
    negative_reviews: Optional[int] = None
    required_age: Optional[int] = None

    # Range Date fields
    release_date_min: Optional[date] = None
    release_date_max: Optional[date] = None

    # Range Numerical fields
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    positive_reviews_min: Optional[int] = None
    positive_reviews_max: Optional[int] = None
    negative_reviews_min: Optional[int] = None
    negative_reviews_max: Optional[int] = None

    @field_validator('platforms')
    def validate_platforms(cls, v):
        if v:
            valid_platforms = {'windows', 'mac', 'linux'}
            v = [platform.lower() for platform in v]
            if not all(platform in valid_platforms for platform in v):
                raise ValueError("Invalid platform. Must be one of: windows, mac, linux")
        return v

# Query API Response Models

class GameResponse(BaseModel):
    app_id: int
    name: str
    release_date: date
    required_age: int
    price: float
    dlc_count: int
    about_the_game: Optional[str]
    supported_languages: List[str]
    platforms: Dict[str, bool]
    positive_reviews: int
    negative_reviews: int
    score_rank: Optional[int]
    developers: List[str]
    publishers: List[str]
    categories: List[str]
    genres: List[str]
    tags: List[str]

class PaginatedResponse(BaseModel):
    page: int
    page_size: int
    total_pages: int
    total_records: int
    results: List[GameResponse]
