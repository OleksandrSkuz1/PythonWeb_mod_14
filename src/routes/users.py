from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.schemas.user import UserResponse, UserSchema
from src.services.auth import auth_service
from src.database.db import get_db


# router = APIRouter(prefix="/users", tags=["users"])
#
#
# @router.get(path="/me", response_model=UserResponse)
# async def get_current_user(user: UserSchema = Depends(auth_service.get_current_user)):
#     return user


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=UserResponse)
async def signup(user: UserSchema, db: AsyncSession = Depends(get_db)):
    async with db.begin():
        result = await db.execute(select(User).filter(User.email == user.email))
        db_user = result.scalar()
        if db_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        new_user = User(
            username=user.username,
            email=user.email,
            password=user.password  # Переконайтеся, що паролі хешуються перед збереженням
        )
        db.add(new_user)

        try:
            await db.commit()
            await db.refresh(new_user)
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Could not create user due to integrity error")

        return new_user