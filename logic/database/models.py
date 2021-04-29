from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, unique=True, nullable=False, index=True)
    name = Column(String, index=True)
    food = relationship('Food', back_populates='user')
    alcohol = relationship('Alcohol', back_populates='user')


class Food(Base):
    __tablename__ = 'food'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    chosen_food = Column(String(100), nullable=False)
    amount = Column(String(50), nullable=False)
    other = Column(String(250))
    wishing_time = Column(DateTime(), nullable=False, default=func.now())

    user = relationship('User', back_populates='food')


class Alcohol(Base):
    __tablename__ = 'alcohol'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, index=True)
    chosen_alcohol = Column(String(100), nullable=False)
    amount = Column(String(50), nullable=False)
    other = Column(String(250))
    wishing_time = Column(DateTime(), nullable=False, default=func.now())

    user = relationship('User', back_populates='alcohol')
