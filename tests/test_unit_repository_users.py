import unittest
from unittest.mock import AsyncMock, patch, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.entity.models import User
from src.repository.users import get_user_by_email, confirmed_email, update_avatar_url, update_token, create_user
from src.schemas.user import UserSchema


class TestAsyncUser(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(
            id=1,
            username="test-user",
            password="password",
            email="test@user.com",
            confirmed=False,
        )
        self.body = UserSchema(
            username="test-user",
            password="password",
            email="test@user.com",
        )
        self.session = AsyncMock(spec=AsyncSession)


    async def test_get_user_by_email(self):
        email = "test@example.com"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = self.user
        self.session.execute.return_value = mock_result

        result = await get_user_by_email(email, db=self.session)
        self.assertEqual(result, self.user)

        # Перевірка, чи однакові запити, а не об'єкти
        expected_query = str(select(User).filter(User.email == email))
        actual_query = str(self.session.execute.call_args[0][0])
        self.assertEqual(expected_query, actual_query)


    @patch('src.repository.users.Gravatar')
    async def test_create_user(self, MockGravatar):
        mock_gravatar_instance = MockGravatar.return_value
        mock_gravatar_instance.get_image.return_value = "avatar_url"

        self.session.add = MagicMock()
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()

        result = await create_user(self.body, self.session)

        self.session.add.assert_called_once()
        self.session.commit.assert_awaited_once()
        self.session.refresh.assert_awaited_once_with(result)

        self.assertIsInstance(result, User)
        self.assertEqual(result.username, self.body.username)
        self.assertEqual(result.email, self.body.email)
        self.assertEqual(result.avatar, "avatar_url")


    async def test_update_token(self):
        token = "new_refresh_token"

        self.session.commit = AsyncMock()

        await update_token(self.user, token, self.session)

        self.assertEqual(self.user.refresh_token, token)
        self.session.commit.assert_awaited_once()

    async def test_confirmed_email(self):
        email = "test@user.com"

        # Підміна get_user_by_email для повернення self.user
        get_user_by_email_mock = AsyncMock(return_value=self.user)
        with patch('src.repository.users.get_user_by_email', get_user_by_email_mock):
            self.session.commit = AsyncMock()

            await confirmed_email(email, self.session)

            get_user_by_email_mock.assert_awaited_once_with(email, self.session)
            self.assertTrue(self.user.confirmed)
            self.session.commit.assert_awaited_once()

    async def test_update_avatar_url(self):
        email = "test@user.com"
        url = "http://new-avatar-url.com/avatar.png"

        # Підміна get_user_by_email для повернення self.user
        get_user_by_email_mock = AsyncMock(return_value=self.user)
        with patch('src.repository.users.get_user_by_email', get_user_by_email_mock):
            self.session.commit = AsyncMock()
            self.session.refresh = AsyncMock()

            result = await update_avatar_url(email, url, self.session)

            get_user_by_email_mock.assert_awaited_once_with(email, self.session)
            self.assertEqual(self.user.avatar, url)
            self.session.commit.assert_awaited_once()
            self.session.refresh.assert_awaited_once_with(self.user)
            self.assertEqual(result, self.user)


if __name__ == '__main__':
    unittest.main()
