from pydantic import BaseModel


class Region(BaseModel):
    region: str


class InstanceLaunchRequest(BaseModel):
    instance_type: str
    ami_id: str
    key_name: str
    security_group_id: str
    region: str = "ap-south-1"


class KeyPairRequest(BaseModel):
    key_name: str
    region: str = "ap-south-1"


class Rule(BaseModel):
    protocol: str = "tcp"
    port: int
    cidr: str = "0.0.0.0/0"


class SecurityGroupRequest(BaseModel):
    group_name: str
    description: str
    vpc_id: str | None = None
    region: str = "ap-south-1"
    rules: list[Rule] = []
