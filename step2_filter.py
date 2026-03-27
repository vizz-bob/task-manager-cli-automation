#!/usr/bin/env python3
"""
Step 2 — Read, filter, and update tasks from local JSON file.

Usage:
    python3 step2_filter.py --status all
    python3 step2_filter.py --status completed
    python3 step2_filter.py --status pending
    python3 step2_filter.py --status pending --output pending_tasks.json
"""

import json
import os
import argparse
from datetime import datetime


def load_tasks(filepath: str) -> list:
    """Load tasks from a JSON file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Tasks file not found: {filepath}")
    with open(filepath, "r") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Expected a JSON array of tasks.")
    return data


def filter_tasks(tasks: list, status: str) -> list:
    """Filter tasks by completion status."""
    if status == "completed":
        return [t for t in tasks if t.get("completed") is True]
    elif status == "pending":
        return [t for t in tasks if t.get("completed") is False]
    return tasks  # "all"


def pretty_print_summary(tasks: list, status: str):
    """Print a formatted summary of tasks to the terminal."""
    print("\n" + "=" * 60)
    print(f"  Task Report — Filter: '{status.upper()}'")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    total = len(tasks)
    completed = sum(1 for t in tasks if t.get("completed"))
    pending = total - completed

    print(f"  Total tasks : {total}")
    print(f"  Completed   : {completed}")
    print(f"  Pending     : {pending}")
    print("-" * 60)

    # Group by userId
    users = sorted(set(t.get("userId", 0) for t in tasks))
    for user_id in users:
        user_tasks = [t for t in tasks if t.get("userId") == user_id]
        done = sum(1 for t in user_tasks if t.get("completed"))
        print(f"\n  User {user_id}: {len(user_tasks)} tasks ({done} done)")
        for task in user_tasks[:5]:  # Show max 5 per user
            status_icon = "✓" if task.get("completed") else "○"
            title = task.get("title", "N/A")[:55]
            print(f"    [{status_icon}] #{task.get('id'):>3}  {title}")
        if len(user_tasks) > 5:
            print(f"    ... and {len(user_tasks) - 5} more")

    print("\n" + "=" * 60)


def save_report(tasks: list, output_path: str, status: str):
    """Save filtered tasks with metadata to a JSON report file."""
    report = {
        "generated_at": datetime.now().isoformat(),
        "filter": status,
        "total_count": len(tasks),
        "tasks": tasks
    }
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n  Report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Filter and report on locally saved tasks from JSONPlaceholder."
    )
    parser.add_argument(
        "--input",
        default="tasks.json",
        help="Path to the input JSON file (default: tasks.json)"
    )
    parser.add_argument(
        "--status",
        choices=["all", "completed", "pending"],
        default="all",
        help="Filter tasks by status (default: all)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to save the filtered report as JSON"
    )
    args = parser.parse_args()

    try:
        tasks = load_tasks(args.input)
        filtered = filter_tasks(tasks, args.status)
        pretty_print_summary(filtered, args.status)

        if args.output:
            save_report(filtered, args.output, args.status)

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("Tip: Run step1_fetch.sh first to download tasks.json")
        raise SystemExit(1)
    except (json.JSONDecodeError, ValueError) as e:
        print(f"\nError reading JSON: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
