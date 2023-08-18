import unittest
from datetime import date
from unittest.mock import AsyncMock, MagicMock, Mock

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Contact
from src.schemas import ContactSchema, ContactResponseSchema
from src.repository.contacts import (
    get_contacts,
    get_contact,
    get_existing_contact,
    create_contact,
    update_contact,
    remove_contact,
    get_by_field,
    birthday_week_contacts,
)


class TestAsync(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = AsyncMock(spec=AsyncSession)
        self.user = User(id=1, email="test@test.com", password="asdasd", confirmed=True)
        self.body = ContactSchema(
            name="asdasd",
            surname="zxczxc",
            email="zxczxc",
            number="123123123",
            bd_date=date(year=2011, month=1, day=1),
            additional_data="zxzxcc",
        )
        self.contact = Contact(
            id=1,
            name="Test1",
            surname="Test1",
            email="Test1@gmail",
            number="123123123",
            bd_date=date(year=2011, month=1, day=1),
            additional_data="zxzxcc",
            user_id=self.user.id,
        )

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        expected_contacts = [Contact(), Contact(), Contact(), Contact()]
        mock_contacts = MagicMock()
        mock_contacts.scalars.return_value.all.return_value = expected_contacts
        self.session.execute.return_value = mock_contacts
        result = await get_contacts(limit, offset, self.user, self.session)
        self.assertEqual(result, expected_contacts)

    async def test_get_contact(self):
        expected_contact = Contact()
        mock_contact = MagicMock()
        mock_contact.scalar_one_or_none.return_value = expected_contact
        self.session.execute.return_value = mock_contact
        result = await get_contact(self.user.id, self.user, self.session)
        self.assertEqual(result, expected_contact)

    async def test_get_existing_contact(self):
        expected_contact = Contact()
        mock_contact = MagicMock()
        mock_contact.scalar_one_or_none.return_value = expected_contact
        self.session.execute.return_value = mock_contact
        result = await get_existing_contact(self.body, self.user, self.session)
        self.assertEqual(result, expected_contact)

    async def test_create_contact(self):
        result = await create_contact(self.body, self.user, self.session)
        self.assertEqual(result.name, self.body.name)
        self.assertEqual(result.surname, self.body.surname)
        self.assertEqual(result.number, self.body.number)
        self.assertEqual(result.bd_date, self.body.bd_date)
        self.assertEqual(result.additional_data, self.body.additional_data)

    async def test_update_contact(self):
        mock_contact = MagicMock()
        mock_contact.scalar_one_or_none.return_value = self.contact
        self.session.execute.return_value = mock_contact

        result = await update_contact(
            self.contact.id, self.body, self.user, self.session
        )

        self.assertEqual(result.name, self.body.name)
        self.assertEqual(result.surname, self.body.surname)
        self.assertEqual(result.number, self.body.number)
        self.assertEqual(result.bd_date, self.body.bd_date)
        self.assertEqual(result.additional_data, self.body.additional_data)

    async def test_remove_contact(self):
        mock_contact = MagicMock()
        mock_contact.scalar_one_or_none.return_value = self.contact
        self.session.execute.return_value = mock_contact

        result = await remove_contact(self.contact.id, self.user, self.session)

        assert result is not None
        assert result.id == self.contact.id