import os
import boto3
from dotenv import load_dotenv


load_dotenv()

ACCESS_KEY = os.getenv("ACCESS_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
BUCKET_NAME = 'tree-tracker-store'
DATA_TYPE = ['drone', 'meteor', 'model', 'parcel', 'planet']


# Function to upload data to S3
def upload_data(file_obj, data_type, object_name=None):
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
            object_name = f'{data_type}/{os.path.basename(file_obj)}'

    # Upload the file
    _s3 = boto3.resource('s3',
                         aws_access_key_id=ACCESS_KEY,
                         aws_secret_access_key=SECRET_KEY)
    bucket = _s3.Bucket(BUCKET_NAME)
    try:
        bucket.upload_file(file_obj, object_name)
    except Exception:
        # print(e)
        return False
    return True


# Function to download data from S3
def download_data(data):
    """
    Download a file from an S3 bucket

    :param data: Data to download
    :return: True if file was downloaded, else False
    """

    _s3 = boto3.resource('s3',
                         aws_access_key_id=ACCESS_KEY,
                         aws_secret_access_key=SECRET_KEY)
    bucket = _s3.Bucket(BUCKET_NAME)

    # Download the file
    if data in DATA_TYPE:
        for obj in bucket.objects.filter(Prefix=data):
            # Check if folder exists
            if not os.path.exists(os.path.dirname(f'data/{obj.key}')):
                os.makedirs(os.path.dirname(f'data/{obj.key}'))
            else:
                # Check if file exists
                if not os.path.isfile(f'data/{obj.key}'):
                    # Download file from S3
                    try:
                        bucket.download_file(obj.key, f'data/{obj.key}')
                        return True
                    except Exception:
                        # print(e)
                        return False
    else:
        return False


# Function to save uploaded file
def save_upload(file_obj, data_type):
    """
    Save uploaded file

    :param file_obj: File to save
    :param data_type: Data type
    :return: File dir if file was saved, else False
    """

    # Check if folder exists
    file_path = f'data/{data_type}/{file_obj.name}'

    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))
    else:
        # Check if file exists
        if not os.path.isfile(file_path):
            # Save file
            try:
                with open(file_path, 'wb') as f:
                    f.write(file_obj.getbuffer())
                return file_path
            except Exception:
                # print(e)
                return False
        else:
            return file_path
