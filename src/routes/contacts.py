from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas import ContactResponseSchema, ContactSchema

from src.repository import contacts as repository_contacts
from src.services.auth import auth_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get(
    "/",
    response_model=List[ContactResponseSchema],
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_contacts(
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0, le=200),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Get a list of contacts.

    Args:
        limit (int): The maximum number of contacts to retrieve.
        offset (int): The offset for pagination.
        db (AsyncSession): The asynchronous database session.
        user (User): The authenticated user.

    Returns:
        List[ContactResponseSchema]: List of contacts.
    """
    contacts = await repository_contacts.get_contacts(limit, offset, user, db)
    return contacts


@router.get(
    "/{contact_id}",
    response_model=ContactResponseSchema,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Get a contact by its ID.

    Args:
        contact_id (int): The ID of the contact.
        db (AsyncSession): The asynchronous database session.
        user (User): The authenticated user.

    Returns:
        ContactResponseSchema: The retrieved contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    contact = await repository_contacts.get_contact(contact_id, user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return contact


@router.post(
    "/",
    response_model=ContactResponseSchema,
    status_code=status.HTTP_201_CREATED,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def create_contact(
    body: ContactSchema,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Create a new contact.

    Args:
        body (ContactSchema): The contact data to create.
        db (AsyncSession): The asynchronous database session.
        user (User): The authenticated user.

    Returns:
        ContactResponseSchema: The created contact.

    Raises:
        HTTPException: If a contact with the same number or email already exists.
    """
    existing_contact = await repository_contacts.get_existing_contact(body, user, db)
    if existing_contact:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contact with this number or email already exists",
        )
    contact = await repository_contacts.create_contact(body, user, db)
    return contact


@router.put(
    "/{contact_id}",
    response_model=ContactResponseSchema,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def update_contact(
    body: ContactSchema,
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Update contact details for the given contact ID.

    Args:
        body (ContactSchema): The updated contact details.
        contact_id (int, optional): The ID of the contact to update.
        db (AsyncSession, optional): The database session.
        user (User, optional): The current user.

    Raises:
        HTTPException: If the contact is not found.

    Returns:
        ContactResponseSchema: The updated contact details.
    """
    contact = await repository_contacts.update_contact(contact_id, body, user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return contact


@router.delete(
    "/{contact_id}",
    response_model=ContactResponseSchema,
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def delete_contact(
    contact_id: int = Path(ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Delete a contact with the given contact ID.

    Args:
        contact_id (int, optional): The ID of the contact to delete.
        db (AsyncSession, optional): The database session.
        user (User, optional): The current user.

    Raises:
        HTTPException: If the contact is not found.

    Returns:
        ContactResponseSchema: The deleted contact details.
    """
    contact = await repository_contacts.remove_contact(contact_id, user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="NOT FOUND",
        )
    return contact


@router.get(
    "/search/{contact_value}",
    response_model=List[ContactResponseSchema],
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_contacts_by_field(
    contact_value: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Retrieve contacts by searching for a specific field value.

    Args:
        contact_value (str): The value to search for in contact fields.
        db (AsyncSession, optional): The database session.
        user (User, optional): The current user.

    Returns:
        List[ContactResponseSchema]: List of contacts matching the search criteria.
    """
    contacts = await repository_contacts.get_by_field(contact_value, user, db)
    return contacts


@router.get(
    "/birthday/next-week",
    response_model=List[ContactResponseSchema],
    description="No more than 10 requests per minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def get_birthday_next_week(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(auth_service.get_current_user),
):
    """
    Retrieve contacts with birthdays in the next week.

    Args:
        db (AsyncSession, optional): The database session.
        user (User, optional): The current user.

    Returns:
        List[ContactResponseSchema]: List of contacts with birthdays in the next week.
    """
    contacts = await repository_contacts.birthday_week_contacts(user, db)
    return contacts
