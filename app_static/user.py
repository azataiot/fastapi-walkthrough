# app_static / user.py
# Created by azat at 8.12.2022

from sqlmodel import Field, SQLModel


class User(SQLModel):
    id = Field(int, primary_key=True)
    username = Field(str, unique=True)
    password = Field(str)
