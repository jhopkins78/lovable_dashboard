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

@router.post("/datasets/upload_dataset")
async def upload_dataset(file: UploadFile = File(...)):
    import os
    filename = os.path.splitext(file.filename)[0]
    table_name = filename.lower().replace(" ", "_")
    timestamp = datetime.utcnow().isoformat() + "Z"
    file_type = os.path.splitext(file.filename)[1][1:]
    file_size = 0
    row_count = 0

    # Step 1: Read file
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    elif file.filename.endswith(".xlsx"):
        df = pd.read_excel(file.file)
    else:
        return {"error": "Unsupported file format"}

    # Step 2: Convert to list-of-dicts for the agent
    records = df.to_dict(orient="records")
    row_count = len(records)
    file.file.seek(0, 2)
    file_size = file.file.tell()

    # Step 2.5: Save DataFrame to disk for persistence
    dataset_id = f"{filename}".lower()
    os.makedirs("./data/uploads", exist_ok=True)
    disk_path = f"./data/uploads/{dataset_id}.csv"
    df.to_csv(disk_path, index=False)
    print(f"[UPLOAD] Dataset saved to disk: {disk_path}")

    # Step 3: Infer schema and create table via agent
    schema = supabase_transformer_agent.infer_schema(records)
    if not supabase_transformer_agent.check_table_exists(table_name):
        supabase_transformer_agent.create_table(table_name, schema)

    # Step 4: Insert data
    supabase_transformer_agent.insert_rows(table_name, records)

    # Step 5: Register or update dataset in registry
    # Use a stable dataset_id based on filename (could be hash or UUID in production)
    existing = [ds for ds in DATASET_REGISTRY.values() if ds["dataset_id"] == dataset_id and ds["created_at"] == timestamp]
    if existing:
        ds = existing[0]
        ds["status"] = "ready"
        ds["row_count"] = row_count
        ds["file_size"] = file_size
    else:
        DATASET_REGISTRY[uuid.uuid4().hex] = {
            "dataset_id": dataset_id,
            "filename": file.filename,
            "status": "ready",
            "created_at": timestamp,
            "row_count": row_count,
            "file_size": file_size,
            "file_type": file_type,
            "used_by_modules": [],
            "disk_path": disk_path
        }

    return {
        "status": "success",
        "rows_inserted": row_count,
        "table": table_name,
        "columns": list(df.columns)
    }
