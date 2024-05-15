from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String(255))
    email = Column(String(255), index=True)
    is_active = Column(Boolean,default=False)


# class Category(Base):
#     __tablename__ = "categories"
#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String(255))

#     videos = relationship("Video",back_populates="category")

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    path = Column(String(255))
    # category_id = Column(Integer, ForeignKey("categories.id"))

    # category = relationship("Category",back_populates="videos")