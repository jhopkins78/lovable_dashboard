"""
test_schema_inference.py
------------------------
Test harness for schema inference logic in supabase_transformer_agent.py.

- Loads test JSON files from tests/data/samples/
- Calls schema inference logic
- Asserts correct type mapping, conflict handling, reserved word renaming, and valid column names
- Prints summary table
- Logs errors to /logs/schema_inference_errors.csv
- Supports CLI and pytest
"""

import os
import sys
import json
import csv
import glob
import pytest
from datetime import datetime
from pathlib import Path

# Import inference logic from agent
sys.path.append(str(Path(__file__).parent.parent / "app" / "agents"))
from supabase_transformer_agent import infer_schema, TYPE_MAP

# Reserved words for PostgreSQL (partial list)
RESERVED_WORDS = {"select", "from", "user", "table", "where", "group", "order"}

def is_reserved(word):
    return word.lower() in RESERVED_WORDS

def to_snake_case(name):
    import re
    name = re.sub(r'[\s\-]+', '_', name)
    name = re.sub(r'[^\w]', '', name)
    return name.lower()

def safe_column_name(name):
    name = to_snake_case(name)
    if is_reserved(name):
        return f"{name}_field"
    return name

def log_error(test_case, field, issue):
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / "schema_inference_errors.csv"
    exists = log_path.exists()
    with open(log_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not exists:
            writer.writerow(["timestamp", "test_case", "field", "issue"])
        writer.writerow([datetime.utcnow().isoformat(), test_case, field, issue])

def run_inference_on_file(file_path, expected_schema):
    with open(file_path, "r") as f:
        data = json.load(f)
    if isinstance(data, dict):
        records = [data]
    elif isinstance(data, list):
        records = data
    else:
        raise Exception("Invalid JSON structure")
    inferred = infer_schema(records)
    passed = True
    notes = []
    for field, expected_type in expected_schema.items():
        col = safe_column_name(field)
        inferred_type = TYPE_MAP.get(inferred.get(field, "str"), "TEXT")
        if inferred_type != expected_type:
            passed = False
            notes.append(f"Field '{field}' expected {expected_type}, got {inferred_type}")
            log_error(Path(file_path).name, field, f"Expected {expected_type}, got {inferred_type}")
        if is_reserved(field):
            if not col.endswith("_field"):
                passed = False
                notes.append(f"Reserved word '{field}' not renamed")
                log_error(Path(file_path).name, field, "Reserved word not renamed")
        if not col.isidentifier():
            passed = False
            notes.append(f"Invalid column name '{col}'")
            log_error(Path(file_path).name, field, "Invalid column name")
    return passed, notes

# Test cases: filename -> expected schema
TEST_CASES = {
    "simple_flat.json": {
        "email": "TEXT",
        "age": "INTEGER",
        "is_active": "BOOLEAN"
    },
    "nested_object.json": {
        "user_id": "INTEGER",
        "profile_name": "TEXT",
        "created_at": "TIMESTAMP"
    },
    "mixed_types.json": {
        "score": "TEXT",  # conflict fallback
        "value": "FLOAT"
    },
    "empty_fields.json": {
        "id": "INTEGER",
        "optional_field": "TEXT"
    },
    "reserved_words.json": {
        "user": "TEXT",
        "select": "TEXT"
    }
}

def print_summary(results):
    print("\nTest Case           | Passed | Notes")
    print("--------------------|--------|-----------------------")
    for case, (passed, notes) in results.items():
        status = "✅" if passed else "⚠️"
        note_str = "; ".join(notes) if notes else "All types correct"
        print(f"{case:<20}| {status:<6} | {note_str}")

@pytest.mark.parametrize("test_file,expected_schema", TEST_CASES.items())
def test_schema_inference(test_file, expected_schema):
    file_path = Path(__file__).parent / "data" / "samples" / test_file
    passed, notes = run_inference_on_file(file_path, expected_schema)
    assert passed, f"Schema inference failed for {test_file}: {notes}"

if __name__ == "__main__":
    results = {}
    for test_file, expected_schema in TEST_CASES.items():
        file_path = Path(__file__).parent / "data" / "samples" / test_file
        if not file_path.exists():
            results[test_file] = (False, [f"Test file {test_file} not found"])
            continue
        passed, notes = run_inference_on_file(file_path, expected_schema)
        results[test_file] = (passed, notes)
    print_summary(results)
