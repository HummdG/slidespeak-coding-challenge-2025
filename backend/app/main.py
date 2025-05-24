import os, uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from tasks import convert_task
from celery.result import AsyncResult

app = FastAPI()

@app.post("/convert")
async def convert(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext != ".pptx":
        raise HTTPException(400, "Only .pptx files supported")
    uid = uuid.uuid4().hex
    local = f"/tmp/{uid}.pptx"
    with open(local, "wb") as f:
        f.write(await file.read())

    # enqueue
    task = convert_task.delay(local)
    return {"jobId": task.id}

@app.get("/status/{job_id}")
def status(job_id: str):
    result = AsyncResult(job_id, app=convert_task.app)
    if result.state == "PENDING":
        return {"status": "processing"}
    elif result.state == "SUCCESS":
        return {"status": "done", **result.result}
    elif result.state in ("FAILURE", "REVOKED"):
        return {"status": "error", "error": str(result.result)}
    else:
        return {"status": result.state.lower()}
