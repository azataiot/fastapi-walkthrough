# sql_app / schemas.py
# Created by azat at 8.12.2022

# Pydantic models (schemas) that will be used when reading data, when returning it from the API.

from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    # For example, before creating an item, we don't know what will be the ID assigned to it,
    # but when reading it (when returning it from the API) we will already know its ID.
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    # the Pydantic model that will be used when reading a user (returning it from the API) doesn't include the password.
    id: int
    is_active: bool
    # when reading a user, we can now declare that items will contain the items that belong to this user.
    items: list[Item] = []

    class Config:
        # This Config class is used to provide configurations to Pydantic. In the Config class,
        # set the attribute orm_mode = True.
        orm_mode = True
