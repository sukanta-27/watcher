# server/models/game_models.py
from sqlalchemy import Column, Integer, String, Date, SmallInteger, Boolean, DECIMAL, Text
from sqlalchemy.orm import relationship
from server.db.base import Base
from .relationship_models import (
    game_developers,
    game_publishers,
    game_categories,
    game_genres,
    game_tags,
    game_languages,
)

class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    release_date = Column(Date, nullable=False)
    required_age = Column(SmallInteger, default=0)
    price = Column(DECIMAL(10, 2), nullable=False) # 10 digits, 2 decimal places
    dlc_count = Column(Integer, default=0)
    positive = Column(Integer, default=0)
    negative = Column(Integer, default=0)
    score_rank = Column(Integer)
    about_the_game = Column(Text)
    windows = Column(Boolean, default=False)
    mac = Column(Boolean, default=False)
    linux = Column(Boolean, default=False)

    developers = relationship('Developer', secondary=game_developers, back_populates='games')
    publishers = relationship('Publisher', secondary=game_publishers, back_populates='games')
    categories = relationship('Category', secondary=game_categories, back_populates='games')
    genres = relationship('Genre', secondary=game_genres, back_populates='games')
    tags = relationship('Tag', secondary=game_tags, back_populates='games')
    languages = relationship('Language', secondary=game_languages, back_populates='games')

class Developer(Base):
    __tablename__ = 'developers'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)

    games = relationship('Game', secondary=game_developers, back_populates='developers')

class Publisher(Base):
    __tablename__ = 'publishers'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)

    games = relationship('Game', secondary=game_publishers, back_populates='publishers')


class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    games = relationship('Game', secondary=game_categories, back_populates='categories')

class Genre(Base):
    __tablename__ = 'genres'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    games = relationship('Game', secondary=game_genres, back_populates='genres')

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    games = relationship('Game', secondary=game_tags, back_populates='tags')

class Language(Base):
    __tablename__ = 'languages'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    games = relationship('Game', secondary=game_languages, back_populates='languages')