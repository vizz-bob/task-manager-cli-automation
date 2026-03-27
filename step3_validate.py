#!/usr/bin/env python3
"""
Step 3 — Fetch tasks from API using requests, validate JSON schema,
and save validated results to disk.

Usage:
    python3 step3_validate.py
    python3 step3_validate.py --output validated_tasks.json
    python3 step3_validate.py --limit 10
"""

import json
import os
import sys
import argparse
from datetime import datetime

try:
    import requests
except ImportError:
    print("Error: 'requests' not installed. Run: pip install requests")
    sys.exit(1)

try:
    import jsonschema
    from jsonschema import validate, ValidationError
except ImportError:
    print("Error: 'jsonschema' not installed. Run: pip install jsonschema")
    sys.exit(1)


# ── Schema Definition ────────────────────────────────────────────────────────
TASK_SCHEMA = {
    "type": "object",
    "required": ["id", "userId", "title", "completed"],
    "properties": {
        "id":        {"type": "integer", "minimum": 1},
        "userId":    {"type": "integer", "minimum": 1},
        "title":     {"type": "string",  "minLength": 1},
        "completed": {"type": "boolean"},
    },
    "additionalProperties": False
}

API_URL = "https://jsonplaceholder.typicode.com/todos"


# ── Fetch ─────────────────────────────────────────────────────────────────────
def fetch_tasks(url: str, timeout: int = 30) -> list:
    """Fetch tasks from the API with error handling."""
    print(f"Fetching tasks from: {url}")
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # raises for 4xx/5xx
    except requests.exceptions.Timeout:
        print(f"Error: Request timed out after {timeout}s")
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Check your internet connection.")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"Error: HTTP error — {e}")
        sys.exit(1)

    print(f"  Status: {response.status_code} OK")
    print(f"  Content-Type: {response.headers.get('Content-Type', 'unknown')}")
    return response.json()


# ── Validate ──────────────────────────────────────────────────────────────────
def validate_tasks(tasks: list) -> tuple[list, list]:
    """
    Validate each task against TASK_SCHEMA.
    Returns (valid_tasks, errors).
    """
    valid = []
    errors = []

    for i, task in enumerate(tasks):
        try:
            validate(instance=task, schema=TASK_SCHEMA)
            valid.append(task)
        except ValidationError as e:
            errors.append({
                "index": i,
                "task_id": task.get("id", "unknown"),
                "error": e.message
            })

    return valid, errors


# ── Report ────────────────────────────────────────────────────────────────────
def print_validation_report(total: int, valid: list, errors: list):
    """Print a validation summary."""
    print("\n" + "=" * 60)
    print("  JSON Schema Validation Report")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print(f"  Total records  : {total}")
    print(f"  Valid          : {len(valid)}")
    print(f"  Invalid        : {len(errors)}")

    if errors:
        print("\n  Validation Errors:")
        for err in errors:
            print(f"    - Task ID {err['task_id']} (index {err['index']}): {err['error']}")
    else:
        print("\n  All records passed schema validation.")

    completed = sum(1 for t in valid if t.get("completed"))
    pending = len(valid) - completed
    print(f"\n  Completed tasks : {completed}")
    print(f"  Pending tasks   : {pending}")
    print("=" * 60)


# ── Save ──────────────────────────────────────────────────────────────────────
def save_results(valid_tasks: list, errors: list, output_path: str):
    """Save validated tasks and any errors to a JSON file."""
    result = {
        "fetched_at": datetime.now().isoformat(),
        "source_url": API_URL,
        "total_valid": len(valid_tasks),
        "total_errors": len(errors),
        "validation_errors": errors,
        "tasks": valid_tasks
    }
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\n  Results saved to: {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Fetch and validate tasks from JSONPlaceholder API."
    )
    parser.add_argument(
        "--output",
        default="validated_tasks.json",
        help="Output file path (default: validated_tasks.json)"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of tasks to process (default: all)"
    )
    args = parser.parse_args()

    tasks = fetch_tasks(API_URL)

    if args.limit:
        tasks = tasks[:args.limit]
        print(f"  Limiting to first {args.limit} tasks.")

    valid_tasks, errors = validate_tasks(tasks)
    print_validation_report(len(tasks), valid_tasks, errors)
    save_results(valid_tasks, errors, args.output)


if __name__ == "__main__":
    main()
