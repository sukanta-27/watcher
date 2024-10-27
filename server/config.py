import os
import dotenv

if os.environ.get("ENV") and os.environ.get("ENV") == "local":
    dotenv.load_dotenv("../.env")

class Settings:
    DATABASE_URL = os.getenv('DATABASE_URL')

    if not DATABASE_URL:
        raise ValueError("No DATABASE_URL environment variable set")
    else:
        print(f"DATABASE_URL loaded from environment variable: {DATABASE_URL}")

settings = Settings()