import asyncio
import logging
from src.database.db import sessionmanager
from src.entity.models import Base
from src.schemas.contact import ContactSchema
from faker import Faker
from src.entity.models import Contact

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fake = Faker()

async def create_fake_contacts(n=10):
    logger.info("Creating database tables...")
    async with sessionmanager._engine.begin() as conn:  # Corrected this line
        await conn.run_sync(Base.metadata.create_all)

    async with sessionmanager.session() as session:  # Corrected this line
        emails_used = set()  # Set of unique emails

        for i in range(n):
            email = fake.unique.email()  # Generate unique email
            while email in emails_used:
                email = fake.unique.email()  # If email is already used, generate a new one
            emails_used.add(email)  # Add email to the set

            contact_data = ContactSchema(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=email,
                phone=fake.phone_number(),
                birthday=fake.date_of_birth(minimum_age=18, maximum_age=60),
                additional_data=fake.text(max_nb_chars=50)  # Generate text up to 50 characters
            )
            db_contact = Contact(**contact_data.dict())
            session.add(db_contact)
            logger.info(f"Added contact {i + 1}/{n}: {contact_data}")

        await session.commit()
        logger.info("All contacts have been added and committed to the database.")

if __name__ == "__main__":
    asyncio.run(create_fake_contacts())


