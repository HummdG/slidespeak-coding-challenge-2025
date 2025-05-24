import os
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import boto3
from tasks import convert_task

app = FastAPI()

# Allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# AWS S3 client
BUCKET = os.getenv("AWS_S3_BUCKET")
REGION = os.getenv("AWS_REGION", "us-east-1")
s3 = boto3.client("s3", region_name=REGION)

@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    # only support .pptx
    ext = os.path.splitext(file.filename)[1].lower()
    if ext != ".pptx":
        raise HTTPException(400, "Only .pptx files supported")

    # Read file bytes
    data = await file.read()
    # Generate a unique S3 key for the PPTX
    s3_key = f"{uuid.uuid4().hex}.pptx"

    # Upload PPTX immediately to S3
    s3.put_object(Bucket=BUCKET, Key=s3_key, Body=data)

    # Enqueue Celery task, passing the S3 key
    task = convert_task.delay(s3_key)
    return {"jobId": task.id}

@app.get("/status/{job_id}")
def status(job_id: str):
    from celery.result import AsyncResult
    result = AsyncResult(job_id, app=convert_task.app)

    if result.state == "PENDING":
        return {"status": "processing"}
    elif result.state == "SUCCESS":
        return {"status": "done", **result.result}
    elif result.state in ("FAILURE", "REVOKED"):
        return {"status": "error", "error": str(result.result)}
    else:
        return {"status": result.state.lower()}
