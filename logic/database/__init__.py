from .models import Base
import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.getenv('CONNECTION_STRING_LOCAL'))
if not database_exists(engine.url):
    create_database(engine.url)

Base.metadata.create_all(engine)

Session = sessionmaker(engine)
session = Session()
