from fastapi import UploadFile, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Picture, User, Role
from src.repository import tags as repository_tags
from src.schemas.images import PictureSchema, PictureUpdateSchema
from src.services.cloudstore import CloudService


async def access_check(user: User, picture_user_id, role):
    """
    Check if the user has access rights to a specific picture based on user ID and role.

    :param user: The user making the access check.
    :type user: User
    :param picture_user_id: The user ID associated with the picture.
    :type picture_user_id: int
    :param role: The role of the user making the access check.
    :type role: Role
    :return: True if the user has access, False otherwise.
    :rtype: bool
    """
    return user.id == picture_user_id or role == Role.admin


async def upload_picture(file: UploadFile, body: PictureSchema, db: AsyncSession, user: User):
    """
    Upload a new picture to the database.

    :param file: The file to be uploaded.
    :type file: UploadFile
    :param body: The schema representing the picture data.
    :type body: PictureSchema
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The user uploading the picture.
    :type user: User
    :return: Information about the uploaded picture.
    :rtype: Dict[str, Union[int, str, List[str], datetime, List[str]]]
    """
    image = await CloudService.upload_picture(user.id, file)
    prepared_tags = []

    if image:
        image_url, public_id = image
        picture = Picture(url=image_url, description=body.description, cloudinary_public_id=public_id, user_id=user.id)

        if body.tags:
            tags = [tag.strip() for tag in body.tags.split(',')]
            if len(tags) > 5:
                await CloudService.delete_picture(public_id)
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Максимальна кількість тегів - 5")
            for tag in tags:
                result = await repository_tags.create_tag(tag, db)
                prepared_tags.append(result)

        for tag_name in prepared_tags:
            picture.tags.append(tag_name)
        db.add(picture)
        await db.commit()
        await db.refresh(picture)

    image_url, _ = image
    stmt = select(Picture).where(Picture.url == image_url)
    picture = await db.execute(stmt)
    picture = picture.unique().scalar_one_or_none()
    return {
        'user_id': picture.user_id,
        'picture_id': picture.id,
        'url': picture.url,
        'description': picture.description,
        'tags': [tag.name for tag in picture.tags],
        'created_at': picture.created_at,
        'comments': picture.comment,
    }


async def delete_picture(picture_id: int, db: AsyncSession, user: User):
    """
    Delete a specific picture from the database.

    :param picture_id: The ID of the picture to delete.
    :type picture_id: int
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The user deleting the picture.
    :type user: User
    :return: Success message.
    :rtype: str
    """
    stmt = select(Picture).where(Picture.id == picture_id)
    picture = await db.execute(stmt)
    picture = picture.unique().scalar_one_or_none()
    if picture:
        if not await access_check(user, picture.user_id, user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='Доступ заборонено: відсутні права на редагування'
            )

        await CloudService.delete_picture(picture.cloudinary_public_id)
        await db.delete(picture)
        await db.commit()
        return 'Success'
    return picture


async def update_picture_description(picture_id: int, body: PictureUpdateSchema, db: AsyncSession, user: User):
    """
    Update the description of a specific picture in the database.

   :param picture_id: The ID of the picture to update.
   :type picture_id: int
   :param body: The schema representing the updated picture data.
   :type body: PictureUpdateSchema
   :param db: The asynchronous database session.
   :type db: AsyncSession
   :param user: The user updating the picture.
   :type user: User
   :return: Information about the updated picture.
   :rtype: Dict[str, Union[int, str, List[str], datetime, List[str]]]
    """
    stmt = select(Picture).where(Picture.id == picture_id)
    picture = await db.execute(stmt)
    picture = picture.unique().scalar_one_or_none()
    if picture:
        if not await access_check(user, picture.user_id, user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='Доступ заборонено: відсутні права на редагування'
            )

        picture.description = body.description
        await db.commit()
        await db.refresh(picture)
        return {
            'user_id': picture.user_id,
            'picture_id': picture.id,
            'url': picture.url,
            'description': picture.description,
            'tags': [tag.name for tag in picture.tags],
            'created_at': picture.created_at,
            'comments': [comment.text for comment in picture.comment],
        }
    return picture


async def get_picture(picture_id: int, db: AsyncSession, user: User):
    """
    Retrieve information about a specific picture from the database.

    :param picture_id: The ID of the picture to retrieve.
    :type picture_id: int
    :param db: The asynchronous database session.
    :type db: AsyncSession
    :param user: The user requesting information about the picture.
    :type user: User
    :return: Information about the picture.
    :rtype: Dict[str, Union[int, str, List[str], datetime, List[str]]]
    """
    stmt = select(Picture).where(Picture.id == picture_id)
    picture = await db.execute(stmt)
    picture = picture.unique().scalar_one_or_none()
    if picture:
        if not await access_check(user, picture.user_id, user.role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail='Доступ заборонено: відсутні права на редагування'
            )

        result = {
            'user_id': picture.user_id,
            'picture_id': picture.id,
            'url': picture.url,
            'description': picture.description,
            'tags': [tag.name for tag in picture.tags],
            'created_at': picture.created_at,
            'comments': [comment.text for comment in picture.comment],
        }
        return result
    return picture
