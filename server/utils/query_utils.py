from sqlalchemy.orm import Query
from sqlalchemy import or_
from typing import List
from server.models import game_models

def apply_platform_filters(query: Query, platforms: List[str]) -> Query:
    platform_filters = []
    for platform in platforms:
        if platform == 'windows':
            platform_filters.append(game_models.Game.windows == True)
        elif platform == 'mac':
            platform_filters.append(game_models.Game.mac == True)
        elif platform == 'linux':
            platform_filters.append(game_models.Game.linux == True)
    return query.filter(or_(*platform_filters))

def apply_multi_value_filters(query: Query, relationship_field, values: List[str], model_field) -> Query:
    filters = [relationship_field.any(model_field.ilike(f'%{value}%')) for value in values]
    return query.filter(or_(*filters))
