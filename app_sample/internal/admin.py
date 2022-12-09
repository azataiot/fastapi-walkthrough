# app_sample/internal / admin.py
# Created by azat at 8.12.2022

from fastapi import APIRouter

router = APIRouter()


@router.post("/")
async def update_admin():
    return {"message": "Admin getting schwifty"}
