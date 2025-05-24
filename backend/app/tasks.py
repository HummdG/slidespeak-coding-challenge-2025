import os, subprocess, uuid
from celery_app import celery
import boto3

s3 = boto3.client("s3")
BUCKET = os.getenv("AWS_S3_BUCKET")
UNOSERVER = f"{os.getenv('UNOSERVER_HOST','unoserver')}:{os.getenv('UNOSERVER_PORT','2002')}"

@celery.task(bind=True)
def convert_task(self, local_filename: str):
    # generate unique names
    uid = uuid.uuid4().hex
    pdf_name = f"{uid}.pdf"
    pptx_name = f"{uid}.pptx"

    # move into temp folder
    os.rename(local_filename, pptx_name)
    # convert via unoserver
    subprocess.run([
        "unoconv",
        "-f", "pdf",
        "-H", UNOSERVER,
        pptx_name
    ], check=True)

    # upload pptx + pdf to S3
    for fname in [pptx_name, pdf_name]:
        s3.upload_file(fname, BUCKET, fname)
        os.remove(fname)

    # generate presigned URL
    url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": pdf_name},
        ExpiresIn=3600
    )
    return {"url": url}
