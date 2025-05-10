import os

from dotenv import load_dotenv
from models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def initialize_db():
    Base.metadata.create_all(engine)


# TODO: turn this script into a class?
# TODO: reorganize folders and files (do I want services or is it overkill for this challenge?)
