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

@router.get("/datasets/list")
async def list_datasets():
    # Stub: Replace with real dataset registry or Supabase query
    print("Received request for /datasets/list")
    datasets = [
        {
            "id": "demo",
            "name": "Sample Deals Dataset",
            "timestamp": "2025-06-01T12:00:00Z",
            "file_type": "csv"
        },
        {
            "id": "test2",
            "name": "Q2 Opportunities",
            "timestamp": "2025-05-15T09:30:00Z",
            "file_type": "xlsx"
        }
    ]
    return {"datasets": datasets}

# Alias: GET /api/datasets returns the same as /api/datasets/list
@router.get("/")
async def list_datasets_alias():
    print("Received request for /datasets (alias for /datasets/list)")
    return await list_datasets()

@router.post("/datasets/upload_dataset")
async def upload_dataset(file: UploadFile = File(...)):
    filename = os.path.splitext(file.filename)[0]
    table_name = filename.lower().replace(" ", "_")

    # Step 1: Read file
    if file.filename.endswith(".csv"):
        df = pd.read_csv(file.file)
    elif file.filename.endswith(".xlsx"):
        df = pd.read_excel(file.file)
    else:
        return {"error": "Unsupported file format"}

    # Step 2: Convert to list-of-dicts for the agent
    records = df.to_dict(orient="records")

    # Step 3: Infer schema and create table via agent
    schema = supabase_transformer_agent.infer_schema(records)
    if not supabase_transformer_agent.check_table_exists(table_name):
        supabase_transformer_agent.create_table(table_name, schema)

    # Step 4: Insert data
    supabase_transformer_agent.insert_rows(table_name, records)

    return {
        "status": "success",
        "rows_inserted": len(records),
        "table": table_name,
        "columns": list(df.columns)
    }
