from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)

    choice = relationship('UserChoice', back_populates='user')


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, unique=True, autoincrement=True, nullable=False)
    parent_id = Column(Integer, ForeignKey('category.id'))
    name = Column(String(50), nullable=False)

    item = relationship('Item', back_populates='category')

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    name = Column(String(50), nullable=False)
    amount = Column(String(50))

    category = relationship('Category', back_populates='item')
    choice = relationship('UserChoice', back_populates='item')

class UserChoice(Base):
    __tablename__ = 'user_choice'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    item_id = Column(Integer, ForeignKey('item.id'), nullable=False)
    datetime = Column(DateTime(), nullable=False, default=func.now())

    user = relationship('User', back_populates='choice')
    item = relationship('Item', back_populates='choice')