# app_static / main.py
# Created by azat at 8.12.2022
import asyncio

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from passlib.context import CryptContext
from jose import JWTError, jwt



SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/private/{file_path}", response_class=FileResponse)
async def read_private_files(file_path: str):
    print(file_path)
    return "static/middleware.svg"


app.mount("/media/public", StaticFiles(directory="media/public"), name="static")
