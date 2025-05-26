import os
import uuid

import boto3
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

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
    if not file.filename:
        raise HTTPException(400, "No filename provided")
    ext = os.path.splitext(file.filename)[1].lower()
    if ext != ".pptx":
        raise HTTPException(400, "Only .pptx files supported")

    # Extract the base filename (without extension)
    base_filename = os.path.splitext(file.filename)[0]

    # Read file bytes
    data = await file.read()

    # Generate unique S3 keys but preserve the original filename structure
    unique_id = uuid.uuid4().hex
    pptx_key = f"{unique_id}_{base_filename}.pptx"

    # Upload PPTX to S3
    s3.put_object(Bucket=BUCKET, Key=pptx_key, Body=data)

    # Enqueue Celery task, passing both the S3 key and the base filename
    task = convert_task.delay(pptx_key, base_filename)
    return {"jobId": task.id}


@app.get("/status/{job_id}")
def status(job_id: str):
    from celery.result import AsyncResult

    result: AsyncResult = AsyncResult(job_id, app=convert_task.app)

    if result.state == "PENDING":
        return {"status": "processing"}
    elif result.state == "SUCCESS":
        task_result = result.result or {}
        if isinstance(task_result, dict):
            return {"status": "done", **task_result}
        else:
            return {"status": "done", "result": task_result}
    elif result.state in ("FAILURE", "REVOKED"):
        return {"status": "error", "error": str(result.result)}
    else:
        return {"status": result.state.lower()}
