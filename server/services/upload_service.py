import aiohttp
import pandas as pd
from sqlalchemy.orm import Session
from server.models.game_models import Game, Developer, Publisher, Category, Genre, Tag, Language
from datetime import datetime
from io import BytesIO
from typing import Tuple, Dict, Any
import ast

def safe_int(value, default=None):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

async def process_csv_from_url(file_url: str, db: Session) -> Tuple[int, int, Dict[Any, str]]:
    errors = {}
    data_to_insert = []

    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status != 200:
                raise Exception(f"Failed to download file: HTTP {response.status}")
            content = await response.read()

    # Read CSV into Pandas DataFrame
    df = pd.read_csv(BytesIO(content), sep=',', dtype=str)
    print(f"DataFrame shape: {df.shape}")
    success_count = 0
    failure_count = 0

    # First Pass: Validate and prepare data
    for index, row in df.iterrows():
        print(f"Validating row {index}")
        try:
            # Parse and validate basic fields
            app_id = safe_int(row['AppID'])
            if app_id is None:
                raise ValueError("AppID is missing or invalid")

            name = row['Name']
            if pd.isna(name):
                raise ValueError("Name is missing")

            release_date_str = row['Release date']
            if pd.isna(release_date_str):
                raise ValueError("Release date is missing")
            try:
                release_date = datetime.strptime(release_date_str, '%b %d, %Y').date()
            except ValueError:
                try:
                    release_date = datetime.strptime(release_date_str, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError(f"Invalid date format for release date: {release_date_str}")

            required_age = safe_int(row['Required age'], 0)
            price = safe_float(row['Price'], 0.0)
            dlc_count = safe_int(row['DLC count'], 0)
            about_the_game = row['About the game'] if pd.notna(row['About the game']) else ''
            windows = str(row['Windows']).strip().upper() == 'TRUE'
            mac = str(row['Mac']).strip().upper() == 'TRUE'
            linux = str(row['Linux']).strip().upper() == 'TRUE'
            positive = safe_int(row['Positive'], 0)
            negative = safe_int(row['Negative'], 0)
            score_rank = safe_int(row['Score rank'], None)

            # Prepare data for insertion
            data_to_insert.append({
                'app_id': app_id,
                'name': name,
                'release_date': release_date,
                'required_age': required_age,
                'price': price,
                'dlc_count': dlc_count,
                'about_the_game': about_the_game,
                'windows': windows,
                'mac': mac,
                'linux': linux,
                'positive': positive,
                'negative': negative,
                'score_rank': score_rank,
                'row_data': row  # Keep original row for related entities
            })

        except Exception as e:
            error_message = f"Error validating row {index}: {e}"
            print(error_message)
            errors[str(index)] = str(e)
            continue

    if errors:
        failure_count = len(errors)
        print(f"Validation failed for {failure_count} rows.")
        if failure_count == len(data_to_insert):
            return success_count, failure_count, errors


    # Second Pass: Insert data into the database within a transaction
    try:
        with db.begin():
            for data in data_to_insert:
                row = data['row_data']
                # Check if game already exists
                game = db.query(Game).filter(Game.app_id == data['app_id']).first()
                if not game:
                    game = Game(
                        app_id=data['app_id'],
                        name=data['name'],
                        release_date=data['release_date'],
                        required_age=data['required_age'],
                        price=data['price'],
                        dlc_count=data['dlc_count'],
                        about_the_game=data['about_the_game'],
                        windows=data['windows'],
                        mac=data['mac'],
                        linux=data['linux'],
                        positive=data['positive'],
                        negative=data['negative'],
                        score_rank=data['score_rank']
                    )
                    db.add(game)
                    db.flush()

                # Process related entities
                process_related_entities(row, game, db)
                success_count += 1

        print(f"Successfully processed {success_count} rows.")

    except Exception as e:
        db.rollback()
        print(f"An error occurred during database insertion: {e}")
        success_count = 0
        failure_count = len(data_to_insert)
        errors['database'] = str(e)

    return success_count, failure_count, errors

def process_related_entities(row, game, db):
    # Developers
    dev_names = row['Developers']
    if pd.notna(dev_names) and dev_names.strip():
        dev_names_list = [dev.strip() for dev in dev_names.split(',') if dev.strip()]
        for dev_name in dev_names_list:
            dev = db.query(Developer).filter(Developer.name == dev_name).first()
            if not dev:
                dev = Developer(name=dev_name)
                db.add(dev)
                db.flush()
            if dev not in game.developers:
                game.developers.append(dev)

    # Publishers
    pub_names = row['Publishers']
    if pd.notna(pub_names) and pub_names.strip():
        pub_names_list = [pub.strip() for pub in pub_names.split(',') if pub.strip()]
        for pub_name in pub_names_list:
            pub = db.query(Publisher).filter(Publisher.name == pub_name).first()
            if not pub:
                pub = Publisher(name=pub_name)
                db.add(pub)
                db.flush()
            if pub not in game.publishers:
                game.publishers.append(pub)

    # Categories
    categories_str = row['Categories']
    if pd.notna(categories_str) and categories_str.strip():
        categories_list = [cat.strip() for cat in categories_str.split(',') if cat.strip()]
        for cat_name in categories_list:
            cat = db.query(Category).filter(Category.name == cat_name).first()
            if not cat:
                cat = Category(name=cat_name)
                db.add(cat)
                db.flush()
            if cat not in game.categories:
                game.categories.append(cat)

    # Genres
    genres_str = row['Genres']
    if pd.notna(genres_str) and genres_str.strip():
        genres_list = [genre.strip() for genre in genres_str.split(',') if genre.strip()]
        for genre_name in genres_list:
            genre = db.query(Genre).filter(Genre.name == genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                db.add(genre)
                db.flush()
            if genre not in game.genres:
                game.genres.append(genre)

    # Tags
    tags_str = row['Tags']
    if pd.notna(tags_str) and tags_str.strip():
        tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        for tag_name in tags_list:
            tag = db.query(Tag).filter(Tag.name == tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.add(tag)
                db.flush()
            if tag not in game.tags:
                game.tags.append(tag)

    # Languages
    langs_str = row['Supported languages']
    if pd.notna(langs_str) and langs_str.strip():
        try:
            supported_languages_list = ast.literal_eval(langs_str)
            if not isinstance(supported_languages_list, list):
                supported_languages_list = [str(supported_languages_list)]
        except (ValueError, SyntaxError):
            supported_languages_list = [langs_str.strip()]
        for lang_name in supported_languages_list:
            lang_name = lang_name.strip()
            if lang_name:
                lang = db.query(Language).filter(Language.name == lang_name).first()
                if not lang:
                    lang = Language(name=lang_name)
                    db.add(lang)
                    db.flush()
                if lang not in game.languages:
                    game.languages.append(lang)
