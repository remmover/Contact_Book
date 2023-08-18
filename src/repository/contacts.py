from datetime import datetime, timedelta

from sqlalchemy import select, extract, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactSchema


async def get_contacts(limit: int, offset: int, user: User, db: AsyncSession):
    """
    Retrieve a list of contacts belonging to a specific user.

    :param limit: Maximum number of contacts to retrieve.
    :param offset: Number of contacts to skip before retrieving.
    :param user: User object representing the owner of the contacts.
    :param db: AsyncSession instance for database operations.
    :return: List of contact objects.
    """
    sq = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(sq)
    return contacts.scalars().all()


async def get_contact(contact_id: int, user: User, db: AsyncSession):
    """
    Retrieve a specific contact belonging to a user.

    :param contact_id: ID of the contact to retrieve.
    :param user: User object representing the owner of the contact.
    :param db: AsyncSession instance for database operations.
    :return: The requested contact object or None if not found.
    """
    sq = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(sq)
    return contact.scalar_one_or_none()


async def get_existing_contact(
    body: ContactSchema,
    user: User,
    db: AsyncSession,
):
    """
    Retrieve an existing contact based on email and number.

    :param body: ContactSchema object containing email and number.
    :param user: User object representing the owner of the contacts.
    :param db: AsyncSession instance for database operations.
    :return: The existing contact object or None if not found.
    """
    sq = select(Contact).filter_by(email=body.email, number=body.number, user=user)
    contact = await db.execute(sq)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, user: User, db: AsyncSession):
    """
    Create a new contact for a user.

    :param body: ContactSchema object containing contact information.
    :param user: User object representing the owner of the contact.
    :param db: AsyncSession instance for database operations.
    :return: The newly created contact object.
    """
    contact = Contact(
        name=body.name,
        surname=body.surname,
        email=body.email,
        number=body.number,
        bd_date=body.bd_date,
        additional_data=body.additional_data,
        user=user,
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(
    contact_id: int, body: ContactSchema, user: User, db: AsyncSession
):
    """
    Update an existing contact's information.

    :param contact_id: ID of the contact to update.
    :param body: ContactSchema object containing updated contact information.
    :param user: User object representing the owner of the contact.
    :param db: AsyncSession instance for database operations.
    :return: The updated contact object or None if not found.
    """
    sq = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(sq)
    contact = result.scalar_one_or_none()
    if contact:
        contact.name = body.name
        contact.surname = body.surname
        contact.email = body.email
        contact.number = body.number
        contact.bd_date = body.bd_date
        contact.additional_data = body.additional_data
        await db.commit()
        await db.refresh(contact)
    return contact


async def remove_contact(contact_id: int, user: User, db: AsyncSession):
    """
    Remove a contact belonging to a user.

    :param contact_id: ID of the contact to remove.
    :param user: User object representing the owner of the contact.
    :param db: AsyncSession instance for database operations.
    :return: The removed contact object or None if not found.
    """
    sq = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(sq)
    contact = result.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def get_by_field(contact_value: str, user: User, db: AsyncSession):
    """
    Retrieve contacts based on a search value (name, surname, or email).

    :param contact_value: Value to search for in name, surname, or email fields.
    :param user: User object representing the owner of the contacts.
    :param db: AsyncSession instance for database operations.
    :return: List of contact objects matching the search value.
    """
    sq = (
        select(Contact)
        .filter_by(user=user)
        .filter(
            (func.lower(Contact.name) == contact_value.lower())
            | (func.lower(Contact.surname) == contact_value.lower())
            | (Contact.email == contact_value)
        )
    )
    contact = await db.execute(sq)
    return contact.scalars()


async def birthday_week_contacts(user: User, db: AsyncSession):
    """
    Retrieve contacts with birthdays in the upcoming week.

    :param user: User object representing the owner of the contacts.
    :param db: AsyncSession instance for database operations.
    :return: List of contact objects with birthdays in the upcoming week.
    """
    today = datetime.today()
    next_week = today + timedelta(days=7)

    sq = (
        select(Contact)
        .filter_by(user=user)
        .filter(
            extract("month", Contact.bd_date).between(today.month, next_week.month),
            extract("day", Contact.bd_date).between(today.day, next_week.day),
        )
    )

    contacts = await db.execute(sq)

    return contacts.scalars().all()
