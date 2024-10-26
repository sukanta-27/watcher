from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from server.db.session import get_db
from server.models.pydantic_models import (
    FilterParams,
    PaginationParams,
    PaginatedResponse,
    GameResponse
)
from server.services.game_service import get_filtered_games
from typing import Optional, List
from datetime import date

router = APIRouter()

@router.get('/query', response_model=PaginatedResponse)
def query_games(
    # Pagination Parameters
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    # Filter Parameters
    name: Optional[str] = Query(None),
    about_the_game: Optional[str] = Query(None),
    developers: Optional[List[str]] = Query(None),
    publishers: Optional[List[str]] = Query(None),
    categories: Optional[List[str]] = Query(None),
    supported_languages: Optional[List[str]] = Query(None),
    genres: Optional[List[str]] = Query(None),
    tags: Optional[List[str]] = Query(None),
    platforms: Optional[List[str]] = Query(None),
    release_date: Optional[date] = Query(None),
    app_id: Optional[int] = Query(None),
    price: Optional[float] = Query(None),
    dlc_count: Optional[int] = Query(None),
    score_rank: Optional[int] = Query(None),
    positive_reviews: Optional[int] = Query(None),
    negative_reviews: Optional[int] = Query(None),
    required_age: Optional[int] = Query(None),
    # Range Filters
    release_date_min: Optional[date] = Query(None),
    release_date_max: Optional[date] = Query(None),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    positive_reviews_min: Optional[int] = Query(None),
    positive_reviews_max: Optional[int] = Query(None),
    negative_reviews_min: Optional[int] = Query(None),
    negative_reviews_max: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    # Manually construct the FilterParams and PaginationParams models
    filters = FilterParams(
        name=name,
        about_the_game=about_the_game,
        developers=developers,
        publishers=publishers,
        categories=categories,
        supported_languages=supported_languages,
        genres=genres,
        tags=tags,
        platforms=platforms,
        release_date=release_date,
        app_id=app_id,
        price=price,
        dlc_count=dlc_count,
        score_rank=score_rank,
        positive_reviews=positive_reviews,
        negative_reviews=negative_reviews,
        required_age=required_age,
        release_date_min=release_date_min,
        release_date_max=release_date_max,
        price_min=price_min,
        price_max=price_max,
        positive_reviews_min=positive_reviews_min,
        positive_reviews_max=positive_reviews_max,
        negative_reviews_min=negative_reviews_min,
        negative_reviews_max=negative_reviews_max
    )
    pagination = PaginationParams(page=page, page_size=page_size)
    try:
        games, total_records, total_pages = get_filtered_games(
            db=db,
            filters=filters,
            pagination=pagination
        )

        # Serialize results
        results = []
        for game in games:
            game_data = GameResponse(
                app_id=game.app_id,
                name=game.name,
                release_date=game.release_date,
                required_age=game.required_age,
                price=game.price,
                dlc_count=game.dlc_count,
                about_the_game=game.about_the_game,
                supported_languages=[language.name for language in game.languages],
                platforms={
                    'windows': game.windows,
                    'mac': game.mac,
                    'linux': game.linux
                },
                positive_reviews=game.positive,
                negative_reviews=game.negative,
                score_rank=game.score_rank,
                developers=[developer.name for developer in game.developers],
                publishers=[publisher.name for publisher in game.publishers],
                categories=[category.name for category in game.categories],
                genres=[genre.name for genre in game.genres],
                tags=[tag.name for tag in game.tags]
            )
            results.append(game_data)

        response = PaginatedResponse(
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
            total_records=total_records,
            results=results
        )

        return response

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
