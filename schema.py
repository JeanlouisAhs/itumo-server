from pydantic import BaseModel
from typing import Optional


class VideoCreate(BaseModel):
    title : str
    path : str
    # description : Optional[str] = None


class Video(VideoCreate):
    id : int
    # category_id  : int

    class Config:
        orm_mode = True
        

# class CategoryCreate(BaseModel):
#     title : str


# class Category(CategoryCreate):
#     id : int
#     videos : list[Video] = []

#     class Config:
#         orm_mode = True


class UserCreate(BaseModel):
    email: str
    name: str 


class User(UserCreate):
    id : int
    is_active : bool

    class Config:
        orm_mode = True
