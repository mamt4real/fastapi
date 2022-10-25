from .. import models, schemas, utils
from fastapi import APIRouter,  status, HTTPException, Depends
from ..database import get_db
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(
    prefix="/users", tags=["Users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
async def create_user(new_user: schemas.UserCreate, db: Session = Depends(get_db)):
    user = new_user.dict()
    user["password"] = utils.hash(user["password"])
    data = models.User(**user)
    db.add(data)
    db.commit()
    db.refresh(data)
    return data


@router.get("/{userID}", status_code=status.HTTP_200_OK, response_model=schemas.User)
def get_user(userID: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == userID).first()

    if not user:
        raise HTTPException(
            status_code=404, detail=f"User with id={userID} not found!")

    return user
