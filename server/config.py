import os

import dotenv

dotenv.load_dotenv("../.env")

class Settings:
    DATABASE_URL = os.environ.get("DATABASE_URL")

settings = Settings()