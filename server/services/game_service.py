from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import List
from server.models import game_models
from server.utils.query_utils import apply_platform_filters, apply_multi_value_filters
from server.models.pydantic_models import FilterParams, PaginationParams

def get_filtered_games(
    db: Session,
    filters: FilterParams,
    pagination: PaginationParams
):
    query = db.query(game_models.Game)

    # Numeric exact matches
    if filters.app_id is not None:
        query = query.filter(game_models.Game.app_id == filters.app_id)
    if filters.required_age is not None:
        query = query.filter(game_models.Game.required_age == filters.required_age)
    if filters.price is not None:
        query = query.filter(game_models.Game.price == filters.price)
    if filters.dlc_count is not None:
        query = query.filter(game_models.Game.dlc_count == filters.dlc_count)
    if filters.positive_reviews is not None:
        query = query.filter(game_models.Game.positive == filters.positive_reviews)
    if filters.negative_reviews is not None:
        query = query.filter(game_models.Game.negative == filters.negative_reviews)
    if filters.score_rank is not None:
        query = query.filter(game_models.Game.score_rank == filters.score_rank)

    # String substring matches
    if filters.name is not None:
        query = query.filter(game_models.Game.name.ilike(f'%{filters.name}%'))
    if filters.about_the_game is not None:
        query = query.filter(game_models.Game.about_the_game.ilike(f'%{filters.about_the_game}%'))

    # Date exact match
    if filters.release_date is not None:
        query = query.filter(game_models.Game.release_date == filters.release_date)

    # Range queries
    if filters.release_date_min is not None:
        query = query.filter(game_models.Game.release_date >= filters.release_date_min)
    if filters.release_date_max is not None:
        query = query.filter(game_models.Game.release_date <= filters.release_date_max)

    if filters.price_min is not None:
        query = query.filter(game_models.Game.price >= filters.price_min)
    if filters.price_max is not None:
        query = query.filter(game_models.Game.price <= filters.price_max)

    if filters.positive_reviews_min is not None:
        query = query.filter(game_models.Game.positive >= filters.positive_reviews_min)
    if filters.positive_reviews_max is not None:
        query = query.filter(game_models.Game.positive <= filters.positive_reviews_max)

    if filters.negative_reviews_min is not None:
        query = query.filter(game_models.Game.negative >= filters.negative_reviews_min)
    if filters.negative_reviews_max is not None:
        query = query.filter(game_models.Game.negative <= filters.negative_reviews_max)

    # Platforms
    if filters.platforms is not None:
        query = apply_platform_filters(query, filters.platforms)

    # Multi-value list fields
    if filters.developers is not None:
        query = apply_multi_value_filters(
            query, game_models.Game.developers, filters.developers, game_models.Developer.name
        )
    if filters.publishers is not None:
        query = apply_multi_value_filters(
            query, game_models.Game.publishers, filters.publishers, game_models.Publisher.name
        )
    if filters.categories is not None:
        query = apply_multi_value_filters(
            query, game_models.Game.categories, filters.categories, game_models.Category.name
        )
    if filters.genres is not None:
        query = apply_multi_value_filters(
            query, game_models.Game.genres, filters.genres, game_models.Genre.name
        )
    if filters.tags is not None:
        query = apply_multi_value_filters(
            query, game_models.Game.tags, filters.tags, game_models.Tag.name
        )
    if filters.supported_languages is not None:
        query = apply_multi_value_filters(
            query, game_models.Game.languages, filters.supported_languages, game_models.Language.name
        )

    # Total records for pagination
    total_records = query.distinct().count()
    total_pages = (total_records + pagination.page_size - 1) // pagination.page_size

    # Pagination
    offset = (pagination.page - 1) * pagination.page_size
    games = (
        query
        .options(
            joinedload(game_models.Game.developers),
            joinedload(game_models.Game.publishers),
            joinedload(game_models.Game.categories),
            joinedload(game_models.Game.genres),
            joinedload(game_models.Game.tags),
            joinedload(game_models.Game.languages)
        )
        .distinct()
        .offset(offset)
        .limit(pagination.page_size)
        .all()
    )

    return games, total_records, total_pages
