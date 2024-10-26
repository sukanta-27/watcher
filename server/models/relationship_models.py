# server/models/relationship_models.py
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from server.db.base import Base

# Association Tables
game_developers = Table(
    'game_developers',
    Base.metadata,
    Column('game_id', Integer, ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
    Column('developer_id', Integer, ForeignKey('developers.id', ondelete='CASCADE'), primary_key=True)
)

game_publishers = Table(
    'game_publishers',
    Base.metadata,
    Column('game_id', Integer, ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
    Column('publisher_id', Integer, ForeignKey('publishers.id', ondelete='CASCADE'), primary_key=True)
)

game_categories = Table(
    'game_categories',
    Base.metadata,
    Column('game_id', Integer, ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id', ondelete='CASCADE'), primary_key=True)
)

game_genres = Table(
    'game_genres',
    Base.metadata,
    Column('game_id', Integer, ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genres.id', ondelete='CASCADE'), primary_key=True)
)

game_tags = Table(
    'game_tags',
    Base.metadata,
    Column('game_id', Integer, ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True)
)

game_languages = Table(
    'game_languages',
    Base.metadata,
    Column('game_id', Integer, ForeignKey('games.id', ondelete='CASCADE'), primary_key=True),
    Column('language_id', Integer, ForeignKey('languages.id', ondelete='CASCADE'), primary_key=True)
)

