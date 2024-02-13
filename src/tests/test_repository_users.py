import unittest
from unittest.mock import patch, AsyncMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User
from src.repository.users import (
    create_user,
    update_token,
    update_avatar,
)
from src.schemas.users import UserSchema


class TestUser(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(id=1, full_name='test_user', password="qwerty", email='test@example.com')

    @patch('src.repository.users.Gravatar')
    @patch('src.repository.users.User')
    async def test_create_user_success(self, MockUser, MockGravatar):
        mock_db_session = AsyncMock()
        mock_gravatar_instance = MockGravatar.return_value
        mock_gravatar_instance.get_image.return_value = 'http://example.com/avatar.jpg'

        user_data = UserSchema(email='test@example.com', full_name='Test User', password='Password')
        mock_user_instance = MockUser.return_value = User(**user_data.model_dump(),
                                                          avatar='http://example.com/avatar.jpg')
        mock_user_instance.email = user_data.email
        mock_user_instance.full_name = user_data.full_name
        mock_user_instance.avatar = 'http://example.com/avatar.jpg'

        mock_select_result = AsyncMock()
        mock_select_result.scalar.return_value = 1
        mock_db_session.scalar = mock_select_result

        with patch('src.repository.users.check_is_first_user', return_value=True):
            created_user = await create_user(user_data, mock_db_session)

        mock_db_session.add.assert_called_once_with(mock_user_instance)
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once_with(mock_user_instance)

        self.assertEqual(created_user.email, user_data.email)
        self.assertEqual(created_user.full_name, user_data.full_name)
        self.assertEqual(created_user.avatar, 'http://example.com/avatar.jpg')

        self.assertEqual(created_user.email, user_data.email)
        self.assertEqual(created_user.full_name, user_data.full_name)
        self.assertEqual(created_user.avatar, 'http://example.com/avatar.jpg')

    @patch('src.repository.users.Gravatar')
    @patch('src.repository.users.User')
    async def test_create_user_with_gravatar_error(self, MockUser, MockGravatar):
        mock_db_session = self.session
        mock_gravatar_instance = MockGravatar.return_value
        mock_gravatar_instance.get_image.side_effect = Exception('Gravatar error')

        user_data = UserSchema(email='test@example.com',
                               full_name='Test User', password='Password')
        mock_user_instance = MockUser.return_value = User(
            **user_data.model_dump(), avatar='http://example.com/avatar.jpg')
        mock_user_instance.email = 'test@example.com'
        mock_user_instance.full_name = 'Test User'

        with self.assertRaises(Exception):
            await create_user(user_data, mock_db_session)
        mock_db_session.add.assert_not_called()
        mock_db_session.commit.assert_not_called()
        mock_db_session.refresh.assert_not_called()

    @patch('src.repository.users.User')
    async def test_update_token(self, Mock_User):
        mock_user = Mock_User.return_value
        token = 'new token'
        await update_token(mock_user, token, self.session)
        self.assertEqual(token, mock_user.refresh_token)
        self.session.commit.assert_called_once()

    @patch('src.repository.users.get_user_by_username', new_callable=AsyncMock)
    async def test_update_avatar(self, MockGetUserByEmail):
        mock_get = MockGetUserByEmail.return_value = User()
        result = await update_avatar('test email', 'test url', self.session, 'public_id')
        self.assertEqual(mock_get.avatar, 'test url')
        self.assertEqual(result.avatar, 'test url')
        self.session.commit.assert_called_once()
        self.assertEqual(result, mock_get)

    # @patch('src.repository.users.get_user_by_username', new_callable=AsyncMock)
    # async def test_update_user(self, MockGetUserByEmail):
    #     user_data = UserUpdate(email='test@example.com', full_name='Test User', password='Passwor')
    #     result = await update_user('test email', user_data, self.session)
    #     self.assertEqual(user_data.email, 'test email')
    #     self.session.commit.assert_called_once()
    #     self.assertEqual(result, user_data)


if __name__ == "__main__":
    unittest.main()
