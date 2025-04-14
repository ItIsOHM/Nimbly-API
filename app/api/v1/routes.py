from typing import Annotated
from fastapi import APIRouter, Query
from app.models.ec2 import InstanceLaunchRequest, KeyPairRequest, Region
from app.services.manager import *

router = APIRouter(prefix="/instance")


@router.get("/")
def describe(region: Region):
    response = describe_instances(region.region)
    return {"response": response}


@router.post("/")
def launch_instance(data: InstanceLaunchRequest):
    result = launch_ec2_instance(data)
    return result


@router.get("/keypair")
def get_keypairs(region: str):
    return get_all_keypairs(region=region)


@router.post("/keypair")
def create_keypair_download(data: KeyPairRequest):
    return create_key_pair_as_file(data.key_name, data.region)


@router.post("/images")
def describe(region: Region):
    response = describe_images(region.region)
    return {"response": response}


@router.get("/identify")
def get_identity():
    identity = identify()
    return {"message": "identified!", "identity": f"{identity}"}


@router.post("/security-group")
def create_sg(data: SecurityGroupRequest):
    return create_security_group(data)
