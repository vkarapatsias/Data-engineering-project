import boto3
import pandas as pd
from io import StringIO
from config.config import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    S3_BUCKET_NAME,
    S3_BASE_KEY,
)
from config.logging_config import logger


def store_to_s3(filePrefix: str, df: pd.DataFrame, windowStr: str):
    """
    Method that uploads the dataframes as CSVs in AWS s3 bucket.
    """

    # Convert DataFrame to CSV string
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    # Configure S3 object
    s3 = boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    S3_KEY = windowStr + "/" + filePrefix + S3_BASE_KEY

    # Upload CSV to S3 bucket
    try:
        s3.put_object(Body=csv_buffer.getvalue(), Bucket=S3_BUCKET_NAME, Key=S3_KEY)
        logger.info(
            f"CSV file uploaded successfully to S3 bucket: {S3_BUCKET_NAME}/{S3_KEY}"
        )
    except Exception as e:
        logger.error(f"Error uploading CSV file to S3: {e}")
        raise Exception(e)
