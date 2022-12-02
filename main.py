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


# =================== Query Parameters =================
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/items/")
async def read_items_query(skip: int = 0, limit: int = 10):
    return fake_items_db[skip:skip + limit]


@app.get("/items_query/{item_id}")
async def read_item_query(item_id: int, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}


# ================ Multiple path and query parameters ==============

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(user_id: int, item_id: int, q: str | None = None, short: bool = False):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item


# ================== Request Body =============================

class Item2(BaseModel):
    name: str
    price: float
    description: str | None = None
    tax: float | None = None


@app.post("/items2/")
async def create_item(item: Item2):
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.put("/items2/{item_id}")
async def create_item2(item_id: int, item: Item2):
    return {"item_id": item_id, **item.dict()}


@app.put("/items22/{item_id}")
async def update_item2(item_id: int, item: Item2, q: str | None = None):
    result = {"item_id": item_id, **item.dict()}
    if q:
        result.update({"q": q})
    return result
