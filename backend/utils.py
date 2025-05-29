import boto3
import os
from botocore.exceptions import NoCredentialsError
from uuid import uuid4

def upload_to_s3(local_file_path):
    s3 = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION")
    )

    bucket_name = os.getenv("S3_BUCKET_NAME")
    s3_key = f"exports/{uuid4().hex}_{os.path.basename(local_file_path)}"

    try:
        s3.upload_file(local_file_path, bucket_name, s3_key)
        s3_url = f"https://{bucket_name}.s3.amazonaws.com/{s3_key}"
        print(f"✅ Uploaded to S3: {s3_url}")
        return s3_url
    except NoCredentialsError as e:
        print("❌ S3 upload failed – no credentials:", e)
        return None
    except Exception as e:
        print("❌ S3 upload failed:", e)
        return None
