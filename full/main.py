# full / main.py
# Created by azat at 9.12.2022


from fastapi import FastAPI
import uvicorn

app = FastAPI()


@app.get("/")
async def read_root():
    return {"hello": "world"}


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
