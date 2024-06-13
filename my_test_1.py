"4 УСПІШНІ"

import unittest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.entity.models import Contact, User
from src.repository.contacts import (
    create_contact, get_all_contacts, get_contact, update_contact, delete_contact, search_contacts, get_upcoming_birthdays
)
from src.schemas.contact import ContactSchema, ContactUpdateSchema


class TestAsyncContact(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.user = User(id=1, username="test-user", password="qwerty")
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_all_contacts(self):
        limit = 10
        offset = 0
        contacts = [
            Contact(id=1, first_name='test_first_name_1', last_name='test_last_name_1', user=self.user),
            Contact(id=2, first_name='test_first_name_2', last_name='test_last_name_2', user=self.user)
        ]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts
        result = await get_all_contacts(limit, offset, self.session, self.user)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact_id = 1
        contact = Contact(id=contact_id, first_name='test_first_name', last_name='test_last_name', user=self.user)
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mocked_contact
        result = await get_contact(contact_id, self.session, self.user)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        body = {
            'first_name': 'test_first_name',
            'last_name': 'test_last_name',
            'email': 'test@test.com',
            'phone': '1234567890',
            'birthday': datetime.today().date(),
            'additional_data': 'Additional data',
            'completed': False
        }
        contact = Contact(
            id=1,
            first_name='test_first_name',
            last_name='test_last_name',
            email='test@test.com',
            phone='1234567890',
            birthday=datetime.today().date(),
            additional_data='Additional data',
            completed=False,
            user=self.user
        )
        self.session.add.return_value = None  # No return value needed for add()
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()
        self.session.refresh.return_value = contact
        result = await create_contact(ContactSchema(**body), self.session, self.user)

        # Використання методу equals для порівняння об'єктів
        self.assertFalse(result.equals(contact))

    async def test_update_contact(self):
        contact_id = 1
        body = {
            'first_name': 'updated_first_name',
            'last_name': 'updated_last_name',
            'email': 'updated_email@test.com',
            'phone': '9876543210',
            'birthday': datetime.today().date(),
            'additional_data': 'Updated additional data',
            'completed': True
        }
        contact = Contact(id=contact_id, first_name='test_first_name', last_name='test_last_name', user=self.user)
        self.session.execute.return_value.scalar_one_or_none.return_value = contact
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()

        # Виклик асинхронної корутини з ключовим словом await
        result = await update_contact(contact_id, ContactUpdateSchema(**body), self.session, self.user)

        updated_contact = Contact(
            id=contact_id,
            first_name='updated_first_name',
            last_name='updated_last_name',
            email='updated_email@test.com',
            phone='9876543210',
            birthday=datetime.today().date(),
            additional_data='Updated additional data',
            completed=True,
            user=self.user
        )

        self.assertContactEqual(result, updated_contact)

    def assertContactEqual(self, contact1, contact2):
        # Порівняння атрибутів об'єктів, додаючи безпечну перевірку на None
        self.assertEqual(contact1.first_name, contact2.first_name)
        self.assertEqual(contact1.last_name, contact2.last_name)
        self.assertEqual(contact1.email, contact2.email)
        self.assertEqual(contact1.phone, contact2.phone)
        self.assertEqual(contact1.birthday, contact2.birthday)
        self.assertEqual(contact1.additional_data, contact2.additional_data)
        self.assertEqual(contact1.completed, contact2.completed)
        self.assertEqual(contact1.user, contact2.user)

    async def test_delete_contact(self):
        # Підготовка даних
        mocked_contact = MagicMock()
        mocked_contact.scalar_one_or_none.return_value = Contact(
            id=1,
            first_name='test_first_name',
            last_name='test_last_name',
            user=self.user,
        )

        self.session.execute.return_value = mocked_contact
        result = await delete_contact(1, self.session, self.user)
        self.session.delete.assert_called_once()
        self.session.commit.assert_called_once()
        self.assertIsInstance(result, Contact)

if __name__ == '__main__':
    unittest.main()

