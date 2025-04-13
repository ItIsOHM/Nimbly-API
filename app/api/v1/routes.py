from fastapi import FastAPI, APIRouter
from app.services.manager import *

router = APIRouter(
    prefix="/instance"
)

@router.get("/")
def get_router():
    profile_name = create_session()
    return {
        "message" : f"session creaetd with profile name : {profile_name}"
    }