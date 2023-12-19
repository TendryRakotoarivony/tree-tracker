import os
from typing import Any, Literal

import boto3  # type: ignore
from dotenv import find_dotenv, load_dotenv
from streamlit.runtime.uploaded_file_manager import UploadedFile

# Load environment variables
load_dotenv(find_dotenv())

ACCESS_KEY: str | None = os.getenv("AWS_ACCESS_KEY_ID")
SECRET_KEY: str | None = os.getenv("AWS_SECRET_ACCESS_KEY")

BUCKET_NAME = "tree-tracker-store"
DATA_TYPE: list[str] = ["drone", "meteor", "model", "parcel", "planet"]


_s3: Any = boto3.resource("s3", aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)  # type: ignore
_s3_bucket: Any = _s3.Bucket(BUCKET_NAME)


# Function to upload data to S3
def upload_data(file_obj: str, data_type: str, object_name: str | None = None) -> bool:
    """
    Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        if data_type in DATA_TYPE:
            object_name = f"{data_type}/{os.path.basename(file_obj)}"

    # Upload the file
    try:
        _s3_bucket.upload_file(file_obj, object_name)
    except Exception:
        # print(e)
        return False
    return True


# Function to download data from S3
def download_data(data: str) -> bool | None:
    """
    Download a file from an S3 bucket

    :param data: Data to download
    :return: True if file was downloaded, else False
    """

    # Download the file
    if data in DATA_TYPE:
        for obj in _s3_bucket.objects.filter(Prefix=data):
            # Check if folder exists
            if not os.path.exists(os.path.dirname(f"data/{obj.key}")):
                os.makedirs(os.path.dirname(f"data/{obj.key}"))
            else:
                # Check if file exists
                if not os.path.isfile(f"data/{obj.key}"):
                    # Download file from S3
                    try:
                        _s3_bucket.download_file(obj.key, f"data/{obj.key}")
                        return True
                    except Exception:
                        # print(e)
                        return False
    else:
        return False


# Function to save uploaded file
def save_upload(file_obj: UploadedFile, data_type: str) -> str | Literal[False] | None:
    """
    Save uploaded file

    :param file_obj: File to save
    :param data_type: Data type
    :return: File dir if file was saved, else False
    """

    # Check if folder exists
    file_path: str = f"data/{data_type}/{file_obj.name}"

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    else:
        # Check if file exists
        if not os.path.isfile(file_path):
            # Save file
            try:
                with open(file_path, "wb") as f:
                    f.write(file_obj.getbuffer())
                return file_path
            except Exception:
                # print(e)
                return False
        else:
            return file_path
