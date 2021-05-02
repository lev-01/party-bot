from .models import Base
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

engine = create_engine(os.getenv('CONNECTION_STRING_LOCAL'), future=True)
# engine = create_engine(os.getenv('CONNECTION_STRING_DOCKER'))

Session = sessionmaker(engine)
if not database_exists(engine.url):
    create_database(engine.url)

Base.metadata.create_all(engine)