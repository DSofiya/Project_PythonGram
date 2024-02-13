from fastapi import APIRouter, Depends, status, Path, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import images as repositories_images
from src.schemas.images import PictureSchema, PictureResponseSchema, PictureUpdateSchema
from src.services.auth import auth_service

router = APIRouter(prefix='/images', tags=['images'])


@router.post("/upload_picture", response_model=PictureResponseSchema, status_code=status.HTTP_201_CREATED)
async def upload_picture(
        file: UploadFile = File(...),
        body: PictureSchema = Depends(PictureSchema),
        db: AsyncSession = Depends(get_db),
        user: User = Depends(auth_service.get_current_user),
):
    """
    Endpoint to upload a new picture.

    :param file: The image file to be uploaded.
    :type file: UploadFile
    :param body: PictureSchema instance containing picture data.
    :type body: PictureSchema
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :param user: Current authenticated user (dependency injection).
    :type user: User
    :return: The uploaded picture.
    :rtype: PictureResponseSchema
    :raises HTTPException: If there is an issue with the upload or authentication fails.
    """
    picture = await repositories_images.upload_picture(file, body, db, user)
    if picture is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail='SOMETHING WENT WRONG')
    return picture


@router.delete("/{picture_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_picture(
        picture_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        user=Depends(auth_service.get_current_user),
):
    """
    Endpoint to delete a specific picture by its ID.

    :param picture_id: ID of the picture to be deleted.
    :type picture_id: int
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :param user: Current authenticated user (dependency injection).
    :type user: User
    :return: No content (HTTP 204).
    :rtype: None
    :raises HTTPException: If the picture is not found or the user lacks the necessary permissions.
    """
    picture = await repositories_images.delete_picture(picture_id, db, user)
    if picture is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='NOT FOUND')
    return picture


@router.patch("/{picture_id}", response_model=PictureResponseSchema)
async def update_picture(
        body: PictureUpdateSchema,
        picture_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        user=Depends(auth_service.get_current_user),
):
    """
    Endpoint to update the description of a specific picture by its ID.

    :param body: PictureUpdateSchema instance containing updated picture data.
    :type body: PictureUpdateSchema
    :param picture_id: ID of the picture to be updated.
    :type picture_id: int
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :param user: Current authenticated user (dependency injection).
    :type user: User
    :return: The updated picture.
    :rtype: PictureResponseSchema
    :raises HTTPException: If the picture is not found.
    """
    picture = await repositories_images.update_picture_description(picture_id, body, db, user)
    if picture is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return picture


@router.get("/{picture_id}", response_model=PictureResponseSchema)
async def get_picture(
        picture_id: int = Path(ge=1),
        db: AsyncSession = Depends(get_db),
        user=Depends(auth_service.get_current_user),
):
    """
    Endpoint to retrieve a specific picture by its ID.

    :param picture_id: ID of the picture to be retrieved.
    :type picture_id: int
    :param db: Asynchronous SQLAlchemy session (dependency injection).
    :type db: AsyncSession
    :param user: Current authenticated user (dependency injection).
    :type user: User
    :return: The retrieved picture.
    :rtype: PictureResponseSchema
    :raises HTTPException: If the picture is not found.
    """
    picture = await repositories_images.get_picture(picture_id, db, user)
    if picture is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="NOT FOUND")
    return picture
