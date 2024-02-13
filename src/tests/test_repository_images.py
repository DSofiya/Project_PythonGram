import unittest
from fastapi import UploadFile
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.conf.config import config
import cloudinary
from pathlib import Path
from src.schemas.images import PictureResponseSchema
from src.entity.models import Picture, User
from src.repository.images import (
    upload_picture,
    delete_picture,
    update_picture_description,
    get_picture,
)


class Testimages(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.session = AsyncMock(spec=AsyncSession)
        self.image = Picture(id=1, url='test', description='testDEADPOOL',
                            created_at=datetime(2000, 3, 12), updated_at=datetime(2000, 3, 13))
        self.images = [
            self.image,
            Picture(
                id=2,
                url=self.image.url,
                description=self.image.description,
                created_at=self.image.created_at,
                updated_at=self.image.updated_at
            ),
            Picture(
                id=3,
                url=self.image.url,
                description=self.image.description,
                created_at=self.image.created_at,
                updated_at=self.image.updated_at
            )
        ]

    async def test_get_image(self):
        mocked_image = MagicMock()
        mocked_image.scalar_one_or_none.return_value = self.image
        self.session.execute.return_value = mocked_image
        result = await get_picture(1, self.session, User())
        self.assertIsNotNone(result, 'Picture object is None')

    
    async def test_create_image(self):
        image_path = Path('logo.png')
        assert image_path.is_file()
        file = UploadFile(filename=image_path.name, file=image_path.open('rb'))
        body = PictureResponseSchema(
            id=1,
            user_id=1,
            url='test',
            description=None,
            tags=['testDEADPOOL', 'Test S'],
            created_at=datetime(2001, 5, 12),
        )

        tags = [tag.strip() for tag in body.tags]
        tags_str = ', '.join(tags)
        body.tags = tags_str

        result = await upload_picture(file, body, self.session, User())
        self.assertEqual(result.url, self.image.url)
        self.assertEqual(result.description, body.description)
        self.assertEqual(result.tags, body.tags)
        self.assertEqual(result.created_at, body.created_at)
        self.assertTrue(hasattr(result, "id"))

    @patch("src.services.cloudstore.CloudService.delete_picture")
    async def test_delete_image(self, mock_delete_picture):
        cloudinary.config(
            cloud_name=config.CLD_NAME,
            api_key=config.CLD_API_KEY,
            api_secret=config.CLD_API_SECRET,
        )

        mocked_image = MagicMock()
        mocked_image.scalar_one_or_none.return_value = self.image
        self.session.execute.return_value = mocked_image

        result = await delete_picture(picture_id=1, db=self.session, user=User())

        self.assertEqual(result, 'Success')


    @patch("src.services.cloudstore.CloudService.delete_picture")
    async def test_delete_image_not_found(self,mock_delete_picture):
        cloudinary.config(
            cloud_name=config.CLD_NAME,
            api_key=config.CLD_API_KEY,
            api_secret=config.CLD_API_SECRET,
        )

        mocked_image = MagicMock()
        mocked_image.scalar_one_or_none.return_value = None
        self.session.execute.return_value = mocked_image

        user = User(id=1, full_name="test_user", password="qwerty", email="test@example.com")
        result = await delete_picture(picture_id=16, db=self.session, user=user)

        self.assertEqual(result,  'Success') 
        
if __name__ == "__main__":
    unittest.main()

