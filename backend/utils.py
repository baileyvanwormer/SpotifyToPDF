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
        # Upload the file (no ACL)
        s3.upload_file(local_file_path, bucket_name, s3_key)

        # Generate a presigned URL
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": s3_key},
            ExpiresIn=3600  # 1 hour
        )

        print(f"✅ Presigned URL: {url}")
        return url

    except NoCredentialsError as e:
        print("❌ S3 upload failed – no credentials:", e)
        return None
    except Exception as e:
        print("❌ S3 upload failed:", e)
        return None
