from typing import Annotated
from fastapi import APIRouter, Query
from app.models.ec2 import InstanceLaunchRequest, KeyPairRequest, Region
from app.services.manager import *

router = APIRouter(prefix="/instance")


@router.get("/identify")
def get_identity():
    identity = identify()
    return {"message": "identified!", "identity": f"{identity}"}


@router.get("/")
def describe(region: Annotated[str, Query()]):
    response = describe_instances(region)
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


@router.delete("/keypair")
def del_keypair(data: KeyPairRequest):
    return delete_keypair(data.key_name, data.region)


@router.get("/images")
def describe(region: str):
    response = describe_images(region)
    return {"response": response}


@router.get("/security-group")
def get_sg(region: Annotated[str, Query()]):
    return get_security_groups(region=region)


@router.get("/security-group/{group_id}")
def get_sg_rules(region: Annotated[str, Query()], group_id: str):
    return get_security_group_rules(region=region, gid=group_id)


@router.post("/security-group")
def create_sg(data: SecurityGroupRequest):
    return create_security_group(data)
