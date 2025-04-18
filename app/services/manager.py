from io import BytesIO
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError, WaiterError
import os
import logging

from fastapi.responses import StreamingResponse

from app.models.ec2 import InstanceLaunchRequest, Region, SecurityGroupRequest

load_dotenv()


def identify():
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )

    try:
        sts = session.client("sts")
        identity = sts.get_caller_identity()
        return identity["Arn"]
    except Exception as e:
        return f"Invalid credentials or failed session: {str(e)}"


def describe_instances(region: str):
    """
    Returns information about your EC2 instances in the given region.
    """
    ec2 = boto3.client(
        "ec2",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=region,
    )
    response = ec2.describe_instances()
    return response


def describe_images(region: str):
    """
    Returns the catalog of AMIs available to your account.
    """
    ec2 = boto3.client("ec2", region_name=region)

    response = ec2.describe_images(
        Owners=["amazon"],
        Filters=[
            {"Name": "architecture", "Values": ["x86_64"]},
            {"Name": "root-device-type", "Values": ["ebs"]},
            {"Name": "virtualization-type", "Values": ["hvm"]},
            {"Name": "name", "Values": ["amzn2-ami-hvm-*-x86_64-gp2"]},
            {"Name": "state", "Values": ["available"]},
        ],
    )
    return response


def launch_ec2_instance(data: InstanceLaunchRequest):
    """Launches an EC2 instance with the provided data."""
    try:
        ec2 = boto3.resource("ec2", region_name=data.region)

        instances = ec2.create_instances(
            ImageId=data.ami_id,
            MinCount=1,
            MaxCount=1,
            InstanceType=data.instance_type,
            KeyName=data.key_name,
            SecurityGroupIds=[data.security_group_id],
        )

        instance = instances[0]
        instance.wait_until_running()
        instance.load()

        return {
            "instance_id": instance.id,
            "state": instance.state["Name"],
            "public_ip": instance.public_ip_address,
        }

    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to launch instance. Check credentials, parameters, and limits.",
        }


def start_ec2_instance(region: str, iid: str):
    try:
        ec2 = boto3.client("ec2", region_name=region)

        ec2.start_instances(InstanceIds=[iid])
        waiter = ec2.get_waiter("instance_running")
        waiter.wait(InstanceIds=[iid])

        return {"instance_id": iid, "state": "running"}

    except Exception as e:
        return {"error": str(e), "message": f"Couldn't start instance: {iid}"}


def stop_ec2_instance(region: str, iid: str):
    try:
        ec2 = boto3.client("ec2", region_name=region)

        ec2.stop_instances(InstanceIds=[iid])
        waiter = ec2.get_waiter("instance_stopped")
        waiter.wait(InstanceIds=[iid])

        return {"instance_id": iid, "state": "stopped"}

    except Exception as e:
        return {"error": str(e), "message": f"Couldn't stop instance: {iid}"}


def terminate_ec2_instance(region: str, iid: str):
    try:
        ec2 = boto3.client("ec2", region_name=region)

        ec2.terminate_instances(InstanceIds=[iid])
        waiter = ec2.get_waiter("instance_terminated")
        waiter.wait(InstanceIds=[iid])

        return {"instance_id": iid, "state": "terminated"}

    except Exception as e:
        return {"error": str(e), "message": f"Couldn't terminate instance: {iid}"}


def create_key_pair_as_file(key_name: str, region: str = "ap-south-1"):
    try:
        ec2 = boto3.client("ec2", region_name=region)

        key_pair = ec2.create_key_pair(KeyName=key_name)

        pem_data = key_pair["KeyMaterial"]

        pem_stream = BytesIO()
        pem_stream.write(pem_data.encode("utf-8"))
        pem_stream.seek(0)

        filename = f"{key_name}.pem"

        return StreamingResponse(
            pem_stream,
            media_type="application/x-pem-file",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        return {"error": str(e), "message": "Couldn't create key pair."}


def create_security_group(data: SecurityGroupRequest):
    try:
        ec2 = boto3.client("ec2", region_name=data.region)

        if not data.vpc_id:
            vpcs = ec2.describe_vpcs()
            data.vpc_id = vpcs["Vpcs"][0]["VpcId"]

        response = ec2.create_security_group(
            GroupName=data.group_name, Description=data.description, VpcId=data.vpc_id
        )

        for rule in data.rules:
            ec2.authorize_security_group_ingress(
                GroupId=response["GroupId"],
                IpProtocol=rule.protocol,
                FromPort=rule.port,
                ToPort=rule.port,
                CidrIp=rule.cidr,
            )

        return {
            "group_id": response["GroupId"],
            "message": "Security group created successfully",
        }

    except Exception as e:
        return {"error": str(e), "message": "Could not create security group"}


def get_all_keypairs(region: str):
    try:
        ec2 = boto3.client("ec2", region_name=region)

        key_pairs = ec2.describe_key_pairs()

        return key_pairs
    except Exception as e:
        return {"error": str(e), "message": "Couldn't create key pair."}


def delete_keypair(key_name: str, region: str):
    try:
        ec2 = boto3.client("ec2", region_name=region)
        response = ec2.delete_key_pair(KeyName=key_name)
        return response
    except Exception as e:
        return {"error": str(e), "message": "Couldn't delete key pair."}


def get_security_groups(region: str):
    try:
        ec2 = boto3.client("ec2", region_name=region)
        response = ec2.describe_security_groups()
        return response
    except Exception as e:
        return {"error": str(e), "message": "Couldn't fetch security group(s)."}


def get_security_group_rules(region: str, gid: str):
    try:
        ec2 = boto3.client("ec2", region_name=region)
        response = ec2.describe_security_group_rules(
            Filters=[{"Name": "group-id", "Values": [gid]}]
        )
        return response
    except Exception as e:
        return {"error": str(e), "message": "Couldn't fetch security group rule(s)."}


def delete_security_group(region: str, gid: str):
    try:
        ec2 = boto3.client("ec2", region_name=region)
        response = ec2.delete_security_group(GroupId=gid)
        return response
    except Exception as e:
        return {"error": str(e), "message": "Couldn't delete security group(s)."}
