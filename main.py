from typing import Union
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root_sync():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item_sync(item_id: int, q: Union[str, None] = None):
    """
    Read a single item synchronously
    :param item_id: int
    :param q: an optional string query parameter
    :return:
    """
    return {"item_id": item_id, "q": q}
