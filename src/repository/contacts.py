from datetime import datetime, timedelta

from sqlalchemy import select, or_, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdateSchema


async def get_all_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    """
    The get_all_contacts function returns a list of contacts for the user.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of records to skip
    :param db: AsyncSession: Pass in the database session
    :param user: User: Filter the contacts by user
    :return: A list of contacts for a user
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user: User):
    """
    The get_contact function returns a contact from the database.

    :param contact_id: int: Specify the id of the contact to be retrieved
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Ensure that the contact belongs to the user making the request
    :return: A contact object
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactSchema: Validate the request body
    :param db: AsyncSession: Pass a database session to the function
    :param user: User: Get the user object from the request
    :return: A contact object
    :doc-author: Trelent
    """
    contact = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User):
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Identify the contact to update
    :param body: ContactUpdateSchema: Pass in the data that will be used to update the contact
    :param db: AsyncSession: Pass in the database session to the function
    :param user: User: Ensure that the user is only updating their own contacts
    :return: A contact object, which is the same as what we get from the create_contact function
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = await result.scalar_one_or_none()

    if contact:
        # Update contact attributes based on body
        for field, value in body.dict().items():
            setattr(contact, field, value)

    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Specify the id of the contact to be deleted
    :param db: AsyncSession: Pass the database session to the function
    :param user: User: Make sure that the user is only deleting their own contacts
    :return: The contact that was deleted
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await db.execute(stmt)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
    return contact


async def search_contacts(db: AsyncSession, query: str):
    """
    The search_contacts function searches the database for contacts that match a given query.

    :param db: AsyncSession: Pass the database session to the function
    :param query: str: Search for contacts by first name, last name or email
    :return: A list of contact objects
    :doc-author: Trelent
    """

    async with db.begin():
        return await db.execute(
            select(Contact).filter(
                or_(
                    Contact.first_name.ilike(f"%{query}%"),
                    Contact.last_name.ilike(f"%{query}%"),
                    Contact.email.ilike(f"%{query}%")
                )
            )
        ).scalars().all()



async def get_upcoming_birthdays(db: AsyncSession):
    """
    The get_upcoming_birthdays function returns a list of contacts whose birthdays are within the next week.

    :param db: AsyncSession: Pass in the database session
    :return: A list of contact objects
    :doc-author: Trelent
    """
    today = datetime.today().date()
    next_week = today + timedelta(days=7)

    result = await db.execute(
        select(Contact).where(
            and_(
                Contact.birthday >= today,
                Contact.birthday <= next_week
            )
        )
    )
    return await result.scalars().all()