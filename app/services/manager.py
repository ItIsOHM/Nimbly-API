from dotenv import load_dotenv
import boto3
import os

load_dotenv()

def create_session():
    session = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
    )

    try:
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        return identity['Arn']
    except Exception as e:
        return f"Invalid credentials or failed session: {str(e)}"
