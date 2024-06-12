import pickle

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi_limiter.depends import RateLimiter

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.schemas.user import UserSchema, UserResponse
from src.services.auth import auth_service

from src.conf.config import config
from src.repository import users as repositories_users


router = APIRouter(prefix="/users", tags=["users"])
cloudinary.config(
    cloud_name=config.CLOUDINARY_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET,
    secure=True,
)


@router.get(
    "/me",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(user: User = Depends(auth_service.get_current_user)):
    """
    The get_current_user function is a dependency that will be injected into the
        get_current_user endpoint. It uses the auth_service to retrieve the current user,
        and returns it if found.

    :param user: User: Tell the function that it expects a user object
    :return: The current user object
    :doc-author: Trelent
    """
    return user


@router.post("/me", response_model=UserResponse)
async def create_user(user: UserSchema, db: AsyncSession = Depends(get_db)):
    """
    The create_user function creates a new user in the database.

    :param user: UserSchema: Validate the request body
    :param db: AsyncSession: Pass in the database session
    :return: A new user object
    :doc-author: Trelent
    """
    async with db.begin():
        result = await db.execute(select(User).filter(User.email == user.email))
        db_user = result.scalar()
        if db_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

        new_user = User(
            username=user.username,
            email=user.email,
            password=user.password
        )
        db.add(new_user)


@router.patch(
    "/avatar",
    response_model=UserResponse,
    dependencies=[Depends(RateLimiter(times=1, seconds=20))],
)
async def get_current_user(
    file: UploadFile = File(),
    user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):

    """
    The get_current_user function is a dependency that returns the current user.
    It uses the auth_service to get the current user from cache or database, and then
    returns it.

    :param file: UploadFile: Get the file from the request body
    :param user: User: Get the current user from the database
    :param db: AsyncSession: Get the database connection
    :param : Get the current user from the database
    :return: The current user
    :doc-author: Trelent
    """
    res = cloudinary.uploader.upload(file.file, public_id=f"GoIT/{user.email}", owerite=True)
    print(res)
    res_url = cloudinary.CloudinaryImage(public_id = f"GoIT/{user.email}").build_url(
        width=250, height=250, crop="fill", version=res.get("version")
    )
    user = await repositories_users.update_avatar_url(user.email, res_url, db)
    auth_service.cache.set(user.email, pickle.dumps(user))
    auth_service.cache.expire(user.email, 300)
    return user


