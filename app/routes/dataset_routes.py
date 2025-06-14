"""
dataset_routes.py
-----------------
Endpoint for uploading datasets, inferring schema, and dynamic table creation in Supabase.
"""

from fastapi import APIRouter, UploadFile, File
import pandas as pd
import os
from app.agents import supabase_transformer_agent

router = APIRouter()

# In-memory dataset registry for demonstration (replace with DB/Supabase in production)
from datetime import datetime
import uuid

DATASET_REGISTRY = {}

def canonicalize_datasets():
    """
    Return only the most current version of each dataset_id.
    Prefer status 'ready', else most recent timestamp.
    """
    by_id = {}
    for ds in DATASET_REGISTRY.values():
        ds_id = ds["dataset_id"]
        if ds_id not in by_id:
            by_id[ds_id] = ds
        else:
            # Prefer 'ready' status, else latest timestamp
            current = by_id[ds_id]
            if ds["status"] == "ready" and current["status"] != "ready":
                by_id[ds_id] = ds
            elif ds["status"] == current["status"]:
                if ds["created_at"] > current["created_at"]:
                    by_id[ds_id] = ds
    return list(by_id.values())

@router.get("/datasets/list")
async def list_datasets():
    print("Received request for /datasets/list")
    datasets = canonicalize_datasets()
    return {"datasets": datasets}

@router.get("/")
async def list_datasets_alias():
    print("Received request for /datasets (alias for /datasets/list)")
    return await list_datasets()

@router.post("/upload_dataset")
@router.post("/upload-files")
async def upload_dataset(file: UploadFile = File(...)):
    import os
    from time import time
    start_time = time()
    filename = os.path.splitext(file.filename)[0]
    dataset_id = f"{filename}".lower()
    timestamp = datetime.utcnow().isoformat() + "Z"
    file_type = os.path.splitext(file.filename)[1][1:]

    # Save file to disk (streaming)
    os.makedirs("./data/uploads", exist_ok=True)
    disk_path = f"./data/uploads/{dataset_id}.csv"
    with open(disk_path, "wb") as out_file:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            out_file.write(chunk)
    print(f"[UPLOAD] Dataset saved to disk: {disk_path}")

    elapsed = time() - start_time
    if elapsed > 5:
        print(f"[UPLOAD] WARNING: Upload+save took {elapsed:.2f}s for {file.filename}")

    # Register minimal metadata (status: processing)
    DATASET_REGISTRY[uuid.uuid4().hex] = {
        "dataset_id": dataset_id,
        "filename": file.filename,
        "status": "processing",
        "created_at": timestamp,
        "file_type": file_type,
        "disk_path": disk_path
    }

    return {
        "dataset_id": dataset_id,
        "status": "processing"
    }
