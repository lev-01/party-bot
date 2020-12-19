from .models import User, Food, Alcohol, Base
from config import POSTGRES_DB, POSTGRES_HOST_LOCAL, POSTGRES_PASSWORD_LOCAL, POSTGRES_USER_LOCAL, POSTGRES_PORT_LOCAL, POSTGRES_HOST
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker

CONN_STRING = f'postgresql://{POSTGRES_USER_LOCAL}:{POSTGRES_PASSWORD_LOCAL}@{POSTGRES_HOST}:{POSTGRES_PORT_LOCAL}/{POSTGRES_DB}'
engine = create_engine(CONN_STRING)
if not database_exists(engine.url):
    create_database(engine.url)

Base.metadata.create_all(engine)

Session = sessionmaker(engine)
session = Session()
