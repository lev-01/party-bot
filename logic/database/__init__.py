from .models import Base, Category
import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from logic.texts import AVAILABLE_FOOD_CATEGORIES, AVAILABLE_ALCOHOL_CATEGORIES

engine = create_engine(os.getenv('CONNECTION_STRING_LOCAL'), future=True)
# engine = create_engine(os.getenv('CONNECTION_STRING_DOCKER'))

Session = sessionmaker(engine)

def init_db():
    if not database_exists(engine.url):
        create_database(engine.url)

        Base.metadata.create_all(engine)
        with Session.begin() as session:
            session.add(Category(name='alcohol'))
            session.add(Category(name='food'))

            for elem in AVAILABLE_ALCOHOL_CATEGORIES:
                session.add(Category(name=elem, parent_id=session.execute(select(Category.id).where(Category.name=='alcohol')).scalars().one()))

            for k, v in AVAILABLE_FOOD_CATEGORIES.items():
                session.add(Category(name=k, parent_id=session.execute(select(Category.id).where(Category.name=='food')).scalars().one()))
                for elem in v:
                    session.add(Category(name=elem, parent_id=session.execute(select(Category.id).where(Category.name==k)).scalars().one()))
        

init_db()