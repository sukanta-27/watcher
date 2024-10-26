# Create a script called create_tables.py in the root directory
from server.db.base import Base
from server.db.session import engine


def create_tables():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")


if __name__ == "__main__":
    create_tables()