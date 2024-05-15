from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import crud, models, schema, process
from database import SessionLocal, engine, Base

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

#Dependency
def get_db():
    db = SessionLocal()
    try : 
        yield db
    finally:
        db.close()


@app.post("/upload-video")
async def upload_video(fileDoc: UploadFile = File(...), title: str = "title"):
    try:
        print("ok")
        subtitles_data = await process.upload(fileDoc, 10, title)
        return JSONResponse(content={"video": subtitles_data}, status_code=200)
    except:
        raise HTTPException(status_code=500, detail="Une erreur a eu lieu")


@app.get("/videos/list")
async def get_videos():
    try:
        list_videos = await process.list_videos()
        return JSONResponse(content={"video": list_videos}, status_code=200)
    except:
        raise HTTPException(status_code=500, detail="Une erreur a eu lieu")
    

@app.post("/users/",response_model=schema.User)
def post_user(user:schema.UserCreate, db:Session=Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db,user=user)


@app.get("/users/", response_model=list[schema.User])
def get_users(skip:int=0, limit:int=3, db:Session=Depends(get_db)):
    users = crud.get_users(db,skip=skip,limit=limit)
    return users


@app.get("/users/{user_id}/",response_model=schema.User)
def get_user(user_id:int, db:Session=Depends(get_db)):
    db_user = crud.get_user(db,user_id =user_id )
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000)