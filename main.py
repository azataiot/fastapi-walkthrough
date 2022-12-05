from datetime import datetime, time, timedelta
from typing import Union
from uuid import UUID

from fastapi import FastAPI, Query, Path, Body, Cookie, Header
from pydantic import BaseModel, Field, HttpUrl, EmailStr, SecretStr
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


# ======================= Query Parameters and String Validators =============================
# Optional query parameters
@app.get("/items-optional/")
async def read_items_optional(q: str | None = Query(default=None, min_length=3, max_length=50, regex="^fixedquery$")):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/items-required/")
async def read_items_optional(q: str = Query(min_length=3, max_length=50, regex="^fixedquery$")):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/items-required-ellipsis/")
async def read_items_optional(q: str = Query(default=..., max_length=5)):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/items-query-list")
async def read_items_query_list(q: list[str] | None = Query(default=None)):
    query_items = {"q": q}
    return query_items


@app.get("/items-query-metadata")
async def read_items_query_metadata(
        q: str | None = Query(
            default=None,
            title="Query String Title",
            description="Query String Description",
            min_length=3, )
):
    results = {"items": [{"item_id": "foo"}, {"item_id": "bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/items-query-alias")
async def read_items_query_alias(q: str | None = Query(default=None, alias="item-query")):
    results = {"items": [{"item_id": "foo"}, {"item_id": "bar"}]}
    if q:
        results.update({"q": q})
    return results


# =================== Path parameters and Numeric validation =================================

@app.get("/items-path-parameters/{item_id}")
async def read_items_path_parameters(
        item_id: int = Path(title="the ID of the item to get"),
        q: str | None = Query(default=None, alias="item-query")):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


# =========================== Body Multiple Parameters =================================

class Item3(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class User3(BaseModel):
    username: str
    full_name: str | None = None


@app.put("/items-body2/{item_id}")
async def update_item3(
        *,  # count the parameters as key word parameters
        item_id: int = Path(title="the ID of the item to update", ge=0, le=1000),
        q: str | None = None,
        item: Item3,
        user: User3,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    if item:
        results.update({"item": item})
    return results


@app.put("/items-importance/{item_id}")
async def update_item(item_id: int, item: Item3, user: User3, importance: int = Body()):
    results = {"item_id": item_id, "item": item, "user": user, "importance": importance}
    return results


# =============== Body Fields =============

class Item4(BaseModel):
    name: str
    description: str | None = Field(
        default=None,
        title="The description of the item",
        max_length=300
    )
    price: float = Field(gt=0, description="The price must be greater than 0")
    tax: float | None = None


@app.put("/items4/{item_id}")
async def update_item4(item_id: int, item: Item4 = Body(embed=True)):
    results = {"item_id": item_id, "item": item}
    return results


# ======================== Body Nested Models =============================
class Item5(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()


@app.put("/items5/{item_id}")
async def update_item(item_id: int, item: Item5):
    results = {"item_id": item_id, "item": item}
    return results


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item6(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: Image | None = None


@app.put("/items6/{item_id}")
async def update_item(item_id: int, item: Item6):
    results = {"item_id": item_id, "item": item}
    return results


class Item7(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    images: list[Image] | None = None


# pure list
@app.post("/images/multiple/")
async def create_multiple_images(images: list[Image]):
    return images


# bodies with arbitrary dict
@app.post("/index-weights/")
async def create_index_weights(weights: dict[int, float]):
    return weights


# ================== Declare Request Example Data =============================

class Item8(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

    class Config:
        schema_extra = {
            "example": {
                "name": "example",
                "description": "example description",
                "price": 10.0,
                "tax": 3.34
            }
        }


@app.put("/items8/{item_id}")
async def update_item8(item_id: int, item: Item8):
    results = {"item_id": item_id, "item": item}
    return results


class Item9(BaseModel):
    name: str = Field(example="Foo")
    description: str | None = Field(default=None, example="A very nice Item")
    price: float = Field(example=35.4)
    tax: float | None = Field(default=None, example=3.2)


@app.put("/items9/{item_id}")
async def update_item8(item_id: int, item: Item9):
    results2 = {"item_id": item_id, "item": item}
    return results2


# ================== Extra Data Types =============================
@app.put("/items10/{item_id}")
async def read_items(
        item_id: UUID,
        start_datetime: datetime | None = Body(default=None),
        end_datetime: datetime | None = Body(default=None),
        repeat_at: time | None = Body(default=None),
        process_after: timedelta | None = Body(default=None),
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "repeat_at": repeat_at,
        "process_after": process_after,
        "start_process": start_process,
        "duration": duration,
    }


# ========= Cookie Parameters =========

@app.get("/items11/")
async def read_items11(ads_id: str | None = Cookie(default=None)):
    print(ads_id)
    return {"ads_id": ads_id}


# ================ Header Parameters ==================
@app.get("/header/")
async def read_header(user_agent: str | None = Header(default=None), x_token: str | None = Header(default=None)):
    return {"User-Agent": user_agent, "X-Token": x_token}


# ================ Response Body ==================
@app.get("/response_body/", response_model=Item8)
async def read_response_body():
    return {"item_id": 1, "name": "Foo", "description": "A very nice Item", "price": 10.0, "tax": 3.34}


class UserIn(BaseModel):
    username: str
    email: EmailStr
    password: SecretStr
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


@app.post("/users/", response_model=UserOut)
async def create_user(user: UserIn):
    return user
