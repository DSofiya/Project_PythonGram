import qrcode
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.entity.models import TransformedPicture, Picture
from src.services.cloudstore import CloudService


class TransformRepository:
    """
    Class for interacting with the database and services for storing and transforming images.

    :param session: Asynchronous SQLAlchemy session object for database interaction.
    :type session: AsyncSession
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transformed_picture(
            self, user_id: int,
            original_picture_id: int,
            transformation_params: dict,
    ):
        """
        Creates a new transformed picture entry in the database.

        :param user_id: User ID associated with the transformed picture.
        :type user_id: int
        :param original_picture_id: ID of the original picture to be transformed.
        :type original_picture_id: int
        :param transformation_params: Dictionary containing transformation parameters.
        :type transformation_params: dict
        :return: The created TransformedPicture object or None if an exception occurs.
        :rtype: TransformedPicture or None
        """
        original_picture = await self.get_picture_by_id(original_picture_id)
        if not original_picture:
            return None
        try:
            transformed_url, public_id = await CloudService.upload_transformed_picture(
                user_id, original_picture.url, transformation_params)
            qr_image = qrcode.make(transformed_url)
            qr_url, qr_public_id = await CloudService.upload_qr_code(user_id, qr_image)
            transformed_picture = TransformedPicture(
                original_picture_id=original_picture_id,
                url=transformed_url,
                public_id=public_id,
                qr_url=qr_url,
                qr_public_id=qr_public_id,
                user_id=user_id,
            )
            self.session.add(transformed_picture)
            await self.session.commit()
            await self.session.refresh(transformed_picture)
            return transformed_picture
        except Exception:
            return None

    async def update_transformed_picture(
            self, transformed_picture_id: int,
            transformation_params: dict,
    ):
        """
        Updates an existing transformed picture entry in the database.

        :param transformed_picture_id: ID of the transformed picture to be updated.
        :type transformed_picture_id: int
        :param transformation_params: Dictionary containing transformation parameters.
        :type transformation_params: dict
        :return: The updated TransformedPicture object or None if an exception occurs.
        :rtype: TransformedPicture or None
        """
        transformed_picture = await self.get_transformed_picture(transformed_picture_id)
        user_id = transformed_picture.user_id
        if not transformed_picture:
            return None
        try:
            new_transformed_url = await CloudService.update_picture_on_cloudinary(
                public_id=transformed_picture.public_id,
                transformation_params=transformation_params
            )
            if not new_transformed_url:
                return None
            new_qr_image = qrcode.make(new_transformed_url)
            new_qr_url, new_qr_public_id = await CloudService.upload_qr_code(user_id, new_qr_image)
            transformed_picture.url = new_transformed_url
            transformed_picture.qr_url = new_qr_url
            transformed_picture.qr_public_id = new_qr_public_id
            self.session.add(transformed_picture)
            await self.session.commit()
            await self.session.refresh(transformed_picture)
            return transformed_picture
        except Exception:
            return None

    async def get_picture_by_id(self, picture_id: int):
        """
        Retrieves a Picture object from the database based on its ID.

        :param picture_id: ID of the picture to be retrieved.
        :type picture_id: int
        :return: The retrieved Picture object or None if not found.
        :rtype: Picture or None
        """
        query = select(Picture).where(Picture.id == picture_id)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_transformed_picture(self, transformed_picture_id: int):
        """
        Retrieves a TransformedPicture object from the database based on its ID.

        :param transformed_picture_id: ID of the transformed picture to be retrieved.
        :type transformed_picture_id: int
        :return: The retrieved TransformedPicture object or None if not found.
        :rtype: TransformedPicture or None
        """
        query = select(TransformedPicture).where(TransformedPicture.id == transformed_picture_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_user_transforms(self, user_id: int):
        """
        Retrieves a list of transformed pictures associated with a specific user.

        :param user_id: User ID for which transformed pictures are to be retrieved.
        :type user_id: int
        :return: List of TransformedPicture objects associated with the user.
        :rtype: list[TransformedPicture]
        """
        query = select(TransformedPicture).where(TransformedPicture.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def delete_transformed_picture(self, transformed_picture_id: int):
        """
        Deletes a transformed picture entry from the database.

        :param transformed_picture_id: ID of the transformed picture to be deleted.
        :type transformed_picture_id: int
        :return: True if the deletion is successful, False otherwise.
        :rtype: bool
        :raises HTTPException: If there is an issue with cloud service operations or a server error occurs.
        """
        query = select(TransformedPicture).where(TransformedPicture.id == transformed_picture_id)
        result = await self.session.execute(query)
        transformed_picture = result.scalars().first()
        if transformed_picture:
            try:
                await CloudService.delete_picture(transformed_picture.public_id)
                await CloudService.delete_picture(transformed_picture.qr_public_id)
                await self.session.delete(transformed_picture)
                await self.session.commit()
            except HTTPException as http_exc:
                raise HTTPException(status_code=http_exc.status_code, detail=http_exc.detail)
            except Exception as e:
                await self.session.rollback()
                raise HTTPException(status_code=500, detail=f"Внутрішня помилка сервера: {e}")
            return True
        return False
