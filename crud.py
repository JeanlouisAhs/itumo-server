from sqlalchemy.orm import Session

import models, schema


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip:int=0, limit:int=100):
    # return db.query(models.User).offset(skip).limit(limit).all()
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user:schema.UserCreate):
    db_user = models.User(email=user.email,
                          name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# def create_category(db: Session, category:schema.CategoryCreate):
#     db_category = models.Category(title=category.title)
#     db.add(db_category)
#     db.commit()
#     db.refresh(db_category)
#     return db_category


def create_video(db: Session, video:schema.VideoCreate):
    db_video = models.Video(title=video.title,
                                path=video.path)
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    return db_video


def get_videos(db: Session, skip:int=0, limit: int=50):
    return db.query(models.Video).offset(skip).limit(limit).all()
