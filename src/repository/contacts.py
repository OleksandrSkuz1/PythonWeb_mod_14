from datetime import datetime, timedelta

from sqlalchemy import select, or_, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact
from src.schemas.contact import ContactSchema, ContactUpdateSchema


async def get_contacts(limit: int, offset: int, db: AsyncSession):
    """
    The get_contacts function returns a list of contacts from the database.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Specify the number of rows to skip before returning results
    :param db: AsyncSession: Pass the database session to the function
    :return: A list of contact objects
    :doc-author: Trelent

    """
    stmt = select(Contact).offset(offset).limit(limit)
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession):
    """
    The get_contact function returns a contact object from the database.

    :param contact_id: int: Specify the id of the contact to be retrieved
    :param db: AsyncSession: Pass the database session to the function
    :return: A contact object, which is a row from the contacts table
    :doc-author: Trelent

    """
    stmt = select(Contact).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession):
    """
    The create_contact function creates a new contact in the database.

    :param body: ContactSchema: Validate the request body and convert it to a contact object
    :param db: AsyncSession: Pass the database session into the function
    :return: The contact object, which is a sqlalchemy model
    :doc-author: Trelent

    """
    contact_data = body.model_dump(exclude_unset=True)
    contact = Contact(**contact_data)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactUpdateSchema, db: AsyncSession):
    """
    The update_contact function updates a contact in the database.

    :param contact_id: int: Specify the contact id to update
    :param body: ContactUpdateSchema: Pass the data from the request body to the function
    :param db: AsyncSession: Pass the database session to the function
    :return: The contact object if it exists
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.additional_data = body.additional_data
        contact.completed = body.completed
        await db.commit()
        await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession):
    """
    The delete_contact function deletes a contact from the database.

    :param contact_id: int: Identify the contact to be deleted
    :param db: AsyncSession: Pass the database session to the function
    :return: The contact that was deleted
    :doc-author: Trelent
    """
    stmt = select(Contact).filter_by(id=contact_id)
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
    async with db.begin():
        result = await db.execute(
            select(Contact).filter(
                or_(
                    and_(
                        extract("month", Contact.birthday) == today.month,
                        extract("day", Contact.birthday) >= today.day,
                        extract("day", Contact.birthday) <= next_week.day,
                    ),
                    and_(
                        extract("month", Contact.birthday) == next_week.month,
                        extract("day", Contact.birthday) >= today.day,
                        extract("day", Contact.birthday) <= next_week.day,
                    ),
                )
            )
        )
        return result.scalars().all()