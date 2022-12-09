from datetime import datetime, time, timedelta
from typing import Union
from uuid import UUID

from fastapi import FastAPI, Query, Path, Body, Cookie, Header, Form, File, UploadFile, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
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


class UserIn0(BaseModel):
    username: str
    email: EmailStr
    password: SecretStr
    full_name: str | None = None


class UserOut0(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


@app.post("/users/", response_model=UserOut0)
async def create_user(user: UserIn0):
    return user


# =========== Extra Models ============
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


def fake_save_user(user_in: UserIn):
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    print("User saved! ..not really")
    return user_in_db


@app.post("/users-extra/", response_model=UserOut)
async def create_user(user_in: UserIn):
    user_saved = fake_save_user(user_in)
    print(user_saved)
    return user_saved


# ============== Response Status Code ==============
@app.post("/items/", status_code=201)
async def create_item(name: str):
    return {"name": name}


# ============== Form Data ===============
@app.post("/login/")
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}


# ============== Request Files ==============
@app.post("/files/")
async def create_file(file: bytes | None = File(default=None, description="A file read as bytes")):
    # whole content will be saved in the memory as bytes
    if not file:
        return {"message": "No file sent"}
    else:
        return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile | None = File(default=None, description="A file read as UploadFile")):
    if not file:
        return {"message": "No upload file sent"}
    else:
        contents = await file.read()
        print(contents)
        return {"filename": file.filename, "content_type": file.content_type, "file": file}


@app.post("/multi-files/")
async def create_multi_files(files: list[bytes] = File(description="Multiple files as bytes")):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/upload-multiple-files/")
async def create_upload_files2(files: list[UploadFile] = File(description="Multiple upload files as UploadFile")):
    return {"filenames": [file.filename for file in files]}


# ============== Request Files and Forms ==============
@app.post("/token-files/")
async def create_file(
        file: bytes = File(), fileb: UploadFile = File(), token: str = Form()
):
    return {
        "file_size": len(file),
        "token": token,
        "fileb_content_type": fileb.content_type,
    }


# ============== Dependencies ==============
async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}


@app.get("/items-depends/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons


@app.get("/users-depends/")
async def read_users(commons: dict = Depends(common_parameters)):
    return commons


class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit


@app.get("/items-common-depends/")
async def read_items(commons: CommonQueryParams = Depends(CommonQueryParams)):
    response = {}
    if commons.q:
        response.update({"q": commons.q})
    items = fake_items_db[commons.skip: commons.skip + commons.limit]
    response.update({"items": items})
    return response


def query_extractor(q: str | None = None):
    return q


def query_or_cookie_extractor(
        q: str = Depends(query_extractor), last_query: str | None = Cookie(default=None)
):
    # If the user didn't provide any query q, we use the last query used, which we saved to a cookie before.
    if not q:
        return last_query
    return q


@app.get("/items12/")
async def read_query(query_or_default: str = Depends(query_or_cookie_extractor)):
    return {"q_or_cookie": query_or_default}


# Dependency in the path operation decorator
async def verify_token(x_token: str = Header()):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: str = Header()):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


@app.get("/items12/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]


# Dependency with yield

async def generate_dep_a():
    pass


async def generate_dep_b():
    pass


async def generate_dep_c():
    pass


async def dependency_a():
    dep_a = generate_dep_a()
    try:
        yield dep_a
    finally:
        dep_a.close()


async def dependency_b(dep_a=Depends(dependency_a)):
    dep_b = generate_dep_b()
    try:
        yield dep_b
    finally:
        dep_b.close(dep_a)


async def dependency_c(dep_b=Depends(dependency_b)):
    dep_c = generate_dep_c()
    try:
        yield dep_c
    finally:
        dep_c.close(dep_b)


# ============== Security ================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# tokenUrl="token" refers to a relative URL token, it's equivalent to ./token


@app.get("/items13/")
async def read_items(token: str = Depends(oauth2_scheme)):
    # This dependency will provide a str that is assigned to the parameter token of the path operation function.
    return {"token": token}


class User4(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


def fake_decode_token(token):
    user = User4(
        username=token + "fake_decoded",
        email="sample@example.com",
        full_name="John Doe",
        disabled=False
    )
    print(user)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    print(token)
    user = fake_decode_token(token)
    print(user)
    return user


@app.get("/users-token/me")
async def read_users_me(current_user: User4 = Depends(get_current_user)):
    return current_user


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}


def fake_hash_password(password: str) -> str:
    return "fakehashed" + password


class UserInDB(User4):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token4(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User4 = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token-old")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(form_data.username)
    print(form_data.password)
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users-secure/me")
async def read_users_me(current_user: User4 = Depends(get_current_active_user)):
    return current_user


# Hashing tokens
from passlib.context import CryptContext
from jose import JWTError, jwt

# to get a string like this run:
# openssl rand -hex 32

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db2 = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User5(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None


class UserInDB5(User5):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user5(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def authenticate_user(fake_db5, username: str, password: str):
    user = get_user(fake_db5, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user5(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db2, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User5 = Depends(get_current_user5)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db2, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users-jwt/me/", response_model=User5)
async def read_users_me(current_user: User5 = Depends(get_current_active_user)):
    return current_user


@app.get("/users/me/items/")
async def read_own_items(current_user: User5 = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]


# ================= Middlewares ========================
from fastapi import FastAPI, Request
import time


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# ============= CORS ================
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/new")
async def main1():
    return {"message": "Hello World"}

# ============ SQL (Relational) Databases =========
