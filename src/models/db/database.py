import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase


DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)


class Base(DeclarativeBase):
    pass