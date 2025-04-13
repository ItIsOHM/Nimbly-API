from fastapi import FastAPI, APIRouter
from app.api.v1.routes import router

app = FastAPI()
app.include_router(router)

@app.get("/")
def home():
    return {
        "message" : "Hello World"
    }