import os
import zipfile
import boto3
import argparse
from datetime import datetime
from botocore.exceptions import NoCredentialsError

ACCESS_KEY = ''
SECRET_KEY = ''
BUCKET = ''


def zip_folder(path, zipped):
    print("zipping {}".format(path))
    for root_folder, dirs, files in os.walk(path):
        for file in files:
            zipped.write(os.path.join(root_folder, file))


def zip_command(folder: str = ""):
    if folder is None or len(folder.strip()) == 0:
        raise Exception("location can't be null")

    filename = 'backup-{}.zip'.format(datetime.now().isoformat())

    zipped = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
    zip_folder(folder, zipped)
    zipped.close()

    upload_to_aws(filename, BUCKET, filename)


def upload_to_aws(local_file, bucket, s3_file):
    print("Uploading")
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-l', '--location', dest='location', help="Folder to Backup", type=str, required=True)
        parser.add_argument('-k', '--key', dest='key', help="Your AWS Key", type=str, required=True)
        parser.add_argument('-s', '--secret', dest='secret', help="Your AWS Secret", type=str, required=True)
        parser.add_argument('-b', '--bucket', dest='bucket', help="Your Bucket", type=str, required=True)

        args = parser.parse_args()
        ACCESS_KEY = args.key
        SECRET_KEY = args.secret
        BUCKET = args.bucket

        zip_command(folder=args.location)
    except Exception as e:
        print(e)
