from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item_sync(item_id: int, q: Union[str, None] = None):
    # optional query parameter q
    """
    Read a single item synchronously
    """
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item_sync(item_id: int, item: Item):
    """
    Update a single item synchronously
    """
    return {"item_name": item.name, "item_id": item_id, "item_price": item.price}


# =================== Path Parameters | Order Matters =====================
@app.get("/users/me")
async def read_user_me():
    return {"user_id": 1, "user_name": "Current username"}


@app.get("/users/{user_id}")
async def read_user(user_id: int):
    return {"user_id": user_id, "user_name": "requested username for {}".format(user_id)}


# =================== Path Parameters | Predefined Values =================


class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = 'resnet'
    lenet = 'lenet'


@app.get("/models/{model_name}")
async def read_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW"}
    elif model_name.value == 'lenet':
        return {"model_name": model_name, "message": "LeCNN all the images"}
    return {"model_name": model_name, "message": "Have some residuals"}
