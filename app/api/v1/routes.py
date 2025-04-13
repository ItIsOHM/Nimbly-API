from fastapi import APIRouter
from app.services.manager import *

router = APIRouter(prefix="/instance")

@router.get("/identify")
def get_identity():
    identity = create_session()
    return {
        "message"   : "session created",
        "identity"  : f"{identity}"
    }

@router.get("/create_resource")
def create_resource():
    result = create_bucket("demo-nimbly")
    return {"buckets": result}
