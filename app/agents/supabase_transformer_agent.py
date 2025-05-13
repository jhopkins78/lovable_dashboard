"""
supabase_transformer_agent.py
-----------------------------
Agent to dynamically create tables in Supabase based on the schema of enriched JSON files.
- Reads /data/enriched/*.json
- Infers schema and maps types to PostgreSQL
- Checks/creates tables in Supabase
- Inserts data
- Logs to /logs/supabase_transform_log.csv
- Supports optional table_overrides.yaml and "target_table" tag
"""

import os
import json
import csv
import glob
import yaml
import httpx
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SCHEMA = "public"

TYPE_MAP = {
    "str": "TEXT",
    "int": "INTEGER",
    "float": "FLOAT",
    "bool": "BOOLEAN",
    "datetime": "TIMESTAMP"
}

def load_table_overrides() -> Dict[str, Any]:
    overrides_path = Path("config/table_overrides.yaml")
    if overrides_path.exists():
        with open(overrides_path, "r") as f:
            return yaml.safe_load(f)
    return {}

def infer_type(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, str):
        # Try to parse datetime
        try:
            from dateutil.parser import parse
            parse(value)
            return "datetime"
        except Exception:
            return "str"
    return "str"

def infer_schema(records: List[Dict[str, Any]]) -> Dict[str, str]:
    schema = {}
    for record in records:
        for k, v in record.items():
            t = infer_type(v)
            if t is None:
                continue
            if k not in schema:
                schema[k] = t
            else:
                # If types conflict, default to TEXT
                if schema[k] != t:
                    schema[k] = "str"
    return schema

def get_table_name(file_path: Path, records: List[Dict[str, Any]], overrides: Dict[str, Any]) -> str:
    # Use "target_table" tag if present in data or overrides
    if records and isinstance(records[0], dict) and "target_table" in records[0]:
        return records[0]["target_table"]
    override = overrides.get(file_path.stem, {}).get("table_name")
    if override:
        return override
    return file_path.stem

def check_table_exists(table_name: str) -> bool:
    url = f"{SUPABASE_URL}/rest/v1/{table_name}?limit=1"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}"
    }
    try:
        resp = httpx.get(url, headers=headers, timeout=10)
        return resp.status_code == 200
    except Exception:
        return False

def create_table(table_name: str, schema: Dict[str, str]):
    columns = []
    for k, t in schema.items():
        pg_type = TYPE_MAP.get(t, "TEXT")
        # Basic reserved word handling
        col = f'"{k}" {pg_type}'
        columns.append(col)
    columns_sql = ", ".join(columns)
    sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_sql});'
    url = f"{SUPABASE_URL}/rest/v1/rpc"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": "execute_sql",
        "args": {"sql": sql}
    }
    # You must have a Postgres function execute_sql(sql text) RETURNS void SECURITY DEFINER
    resp = httpx.post(url, headers=headers, json=payload, timeout=20)
    if resp.status_code not in (200, 201, 204):
        raise Exception(f"Failed to create table: {resp.text}")

def insert_rows(table_name: str, records: List[Dict[str, Any]]):
    url = f"{SUPABASE_URL}/rest/v1/{table_name}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    resp = httpx.post(url, headers=headers, json=records, timeout=30)
    if resp.status_code not in (200, 201, 204):
        raise Exception(f"Failed to insert rows: {resp.text}")

def log_transform(file: str, table: str, status: str, count: int, error: Optional[str] = None):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / "supabase_transform_log.csv"
    exists = log_path.exists()
    with open(log_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not exists:
            writer.writerow(["timestamp", "file", "table", "status", "count", "error"])
        writer.writerow([datetime.utcnow().isoformat(), file, table, status, count, error or ""])

def process_file(file_path: Path, overrides: Dict[str, Any]):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        # Accept list of dicts or single dict
        if isinstance(data, dict):
            records = [data]
        elif isinstance(data, list):
            records = data
        else:
            raise Exception("Invalid JSON structure")
        table_name = get_table_name(file_path, records, overrides)
        schema = infer_schema(records)
        # Apply field renaming/type forcing from overrides
        table_override = overrides.get(file_path.stem, {})
        if "fields" in table_override:
            for orig, new in table_override["fields"].items():
                if orig in schema:
                    schema[new["name"]] = new.get("type", schema[orig])
                    del schema[orig]
                    for r in records:
                        if orig in r:
                            r[new["name"]] = r.pop(orig)
        # Check/create table
        if not check_table_exists(table_name):
            create_table(table_name, schema)
        # Insert data
        insert_rows(table_name, records)
        log_transform(str(file_path), table_name, "success", len(records))
    except Exception as e:
        log_transform(str(file_path), "unknown", "fail", 0, str(e))

def run_supabase_transformer():
    overrides = load_table_overrides()
    files = glob.glob("data/enriched/*.json")
    for file in files:
        process_file(Path(file), overrides)
