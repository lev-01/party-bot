from .models import User, Food, Alcohol, Base
from config import CONN_STRING
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker

engine = create_engine(CONN_STRING)
if not database_exists(engine.url):
    create_database(engine.url)

Base.metadata.create_all(engine)

Session = sessionmaker(engine)
session = Session()
