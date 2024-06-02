from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class ContactSchema(BaseModel):
    first_name: str = Field(min_length=1, max_length=25)
    last_name: str = Field(min_length=1, max_length=25)
    email: str = Field(min_length=1, max_length=50)
    phone: str = Field(min_length=1, max_length=50)
    birthday: date
    additional_data: str = Field(min_length=1, max_length=50)
    completed: Optional[bool] = False


class ContactUpdateSchema(ContactSchema):
    completed: bool


class ContactResponse(BaseModel):
    id: int = 1
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: date
    additional_data: str = None
    completed: bool

    class Config:
        from_attributes = True