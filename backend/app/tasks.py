import os
import uuid
import boto3
import requests
from celery_app import celery

# Configuration from environment
BUCKET     = os.getenv("AWS_S3_BUCKET")
REGION     = os.getenv("AWS_REGION", "us-east-1")
UNOSERVER  = os.getenv("UNOSERVER_HOST", "unoserver")
PORT       = os.getenv("UNOSERVER_PORT", "2004")

# Initialize S3 client
s3 = boto3.client("s3", region_name=REGION)

@celery.task(bind=True)
def convert_task(self, pptx_key: str):
    """
    1) Download PPTX from S3
    2) Send it to Unoserver via its /request endpoint
    3) Save returned PDF to /tmp
    4) Upload PDF back to S3 & return a presigned URL
    """
    # Generate unique filenames / keys
    uid        = uuid.uuid4().hex
    local_pptx = f"/tmp/{uid}.pptx"
    local_pdf  = f"/tmp/{uid}.pdf"
    pdf_key    = f"{uid}.pdf"

    # 1) Download PPTX from S3
    s3.download_file(BUCKET, pptx_key, local_pptx)

    # 2) POST to Unoserver's /request endpoint
    with open(local_pptx, "rb") as pptx_file:
        response = requests.post(
            f"http://{UNOSERVER}:{PORT}/request",
            files={"file": pptx_file},
            data={"convert-to": "pdf"},
            timeout=300
        )
    response.raise_for_status()  # will raise HTTPError on non-2xx

    # 3) Write the PDF content to a local file
    with open(local_pdf, "wb") as pdf_out:
        pdf_out.write(response.content)

    # 4) Upload the PDF back to S3
    s3.upload_file(local_pdf, BUCKET, pdf_key)

    # Cleanup local temp files
    os.remove(local_pptx)
    os.remove(local_pdf)
    # Optionally remove original PPTX from S3:
    # s3.delete_object(Bucket=BUCKET, Key=pptx_key)

    # Generate a presigned URL valid for 1 hour
    presigned_url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": pdf_key},
        ExpiresIn=3600
    )

    return {"url": presigned_url}