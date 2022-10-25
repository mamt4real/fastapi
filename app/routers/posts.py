from .. import models, schemas, oauth2
from fastapi import Body, APIRouter, Response, status, HTTPException, Depends
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import List

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), limit: int = 10, page: int = 1):
    query = db.query(models.Post, func.count(
        models.Vote.post_id).label("votes"))
    query = query.join(models.Vote, models.Post.id ==
                       models.Vote.post_id, isouter=True)
    query = query.order_by(text("posts.created_at DESC"))
    query = query.group_by(models.Post.id).limit(
        limit).offset((page - 1) * limit)
    posts = query.all()
    return posts


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
async def add_post(new_post: schemas.PostCreate, db: Session = Depends(get_db), user=Depends(oauth2.get_current_user)):
    post = new_post.dict()
    post["user_id"] = user.id
    data = models.Post(**post)
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


@router.get("/my-posts", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db), user=Depends(oauth2.get_current_user), limit: int = 10):
    posts = db.query(models.Post).filter(
        models.Post.user_id == user.id).limit(limit).all()
    return posts


@router.get("/{postID}", response_model=schemas.Post)
async def get_post(postID: int, db: Session = Depends(get_db)):

    post = db.query(models.Post).filter(models.Post.id == postID).first()
    if not post:
        raise HTTPException(
            status_code=404, detail=f"Post with id={postID} not found!")
    return post


@router.patch("/{postID}", status_code=status.HTTP_200_OK, response_model=schemas.Post)
async def update_post(postID: int, data: dict = Body(...),  db: Session = Depends(get_db), user=Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == postID)

    if not post.first():
        raise HTTPException(
            status_code=404, detail=f"Post with id={postID} not found!")
    if post.first().user_id != user.id:
        raise HTTPException(
            status_code=403, detail=f"You can't update a post you did'nt create")
    post.update(data)
    db.commit()
    return post.first()


@router.delete("/{postID}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(postID: int, db: Session = Depends(get_db), user=Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == postID)
    if not post.first():
        raise HTTPException(
            status_code=404, detail=f"Post with id={postID} not found!")
    if post.first().user_id != user.id:
        raise HTTPException(
            status_code=403, detail=f"You can't delete a post you did'nt create")

    post.delete(synchronize_session=False)
    db.commit()
    return
