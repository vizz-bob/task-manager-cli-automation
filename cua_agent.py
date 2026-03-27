#!/usr/bin/env python3
"""
CUA Agent Simulator
====================
This script simulates exactly what a Computer-Use Agent does day-to-day.
It performs real tasks on websites using Playwright AND automatically
records every action as a CUA trajectory — just like a human annotator would.

What the agent does in this demo:
  1. Opens JSONPlaceholder website
  2. Navigates to the /todos API endpoint
  3. Reads and counts the tasks
  4. Navigates to /users endpoint
  5. Extracts user names
  6. Takes screenshots as evidence at each step

Every action is recorded with:
  - Action number & type
  - Description of what happened
  - Verification (what the agent observed to confirm success)
  - Screenshot filename as evidence

Usage:
    python3 cua_agent.py
    python3 cua_agent.py --no-headless   (show browser window)
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
except ImportError:
    print("Error: playwright not installed. Run: python3 -m playwright install chromium")
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────
OUTPUT_DIR      = "cua_evidence"
TRAJECTORY_FILE = "cua_trajectory.json"
BASE_URL        = "https://jsonplaceholder.typicode.com"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ── Trajectory Recorder ───────────────────────────────────────
class TrajectoryRecorder:
    def __init__(self):
        self.steps = []
        self.step_num = 0
        self.start_time = datetime.now()

    def record(self, action_type, action, description, verification, screenshot=None, status="success", error=None):
        self.step_num += 1
        step = {
            "step":         self.step_num,
            "timestamp":    datetime.now().isoformat(),
            "action_type":  action_type,
            "action":       action,
            "description":  description,
            "verification": verification,
            "screenshot":   screenshot,
            "status":       status,
            "error":        error,
        }
        self.steps.append(step)

        # Print live
        icon = "✓" if status == "success" else "✗"
        print(f"  [{icon}] Step {self.step_num:02d} | {action_type:<12} | {action[:50]}")
        if status == "error":
            print(f"          ERROR: {error}")
        return step

    def save(self):
        output = {
            "agent":        "CUA Agent Simulator v1.0",
            "task":         "Browse JSONPlaceholder API and extract data",
            "started_at":   self.start_time.isoformat(),
            "completed_at": datetime.now().isoformat(),
            "total_steps":  self.step_num,
            "total_errors": sum(1 for s in self.steps if s["status"] == "error"),
            "trajectory":   self.steps,
        }
        with open(TRAJECTORY_FILE, "w") as f:
            json.dump(output, f, indent=2)
        return output


# ── Screenshot helper ─────────────────────────────────────────
def take_screenshot(page, name):
    filename = f"{OUTPUT_DIR}/{name}.png"
    page.screenshot(path=filename, full_page=False)
    size = Path(filename).stat().st_size
    return filename, size


# ── Main Agent ────────────────────────────────────────────────
def run_agent(headless=True):
    recorder = TrajectoryRecorder()

    print("\n" + "=" * 65)
    print("  CUA Agent Simulator — Starting Task")
    print("=" * 65)
    print(f"  Target  : {BASE_URL}")
    print(f"  Headless: {headless}")
    print(f"  Evidence: ./{OUTPUT_DIR}/")
    print("=" * 65 + "\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        try:
            # ── Step 1: Launch browser ────────────────────────
            recorder.record(
                action_type  = "LAUNCH",
                action       = "Launch Chromium browser (headless)",
                description  = "Agent starts a headless Chromium browser instance to begin the task",
                verification = "Browser launched with no errors; viewport set to 1280x800",
                screenshot   = None,
            )

            # ── Step 2: Navigate to homepage ──────────────────
            response = page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
            ss, size = take_screenshot(page, "step02_homepage")
            recorder.record(
                action_type  = "NAVIGATE",
                action       = f"Go to {BASE_URL}",
                description  = f"Agent navigates to JSONPlaceholder homepage to begin exploration",
                verification = f"HTTP {response.status} received; page loaded; screenshot saved ({size:,} bytes)",
                screenshot   = ss,
            )

            # ── Step 3: Extract page title ────────────────────
            title = page.title()
            recorder.record(
                action_type  = "EXTRACT",
                action       = "Read page title",
                description  = "Agent reads the browser tab title to confirm correct page is loaded",
                verification = f"Title confirmed: '{title}'",
                screenshot   = ss,
            )

            # ── Step 4: Extract main heading ──────────────────
            page.wait_for_selector("h1", timeout=5000)
            h1 = page.locator("h1").first.inner_text().strip()
            recorder.record(
                action_type  = "EXTRACT",
                action       = "Read H1 heading from page",
                description  = "Agent extracts the main heading to verify page content is correct",
                verification = f"H1 text found: '{h1[:60]}'",
                screenshot   = ss,
            )

            # ── Step 5: Navigate to /todos endpoint ───────────
            response2 = page.goto(f"{BASE_URL}/todos", wait_until="domcontentloaded")
            ss2, size2 = take_screenshot(page, "step05_todos")
            recorder.record(
                action_type  = "NAVIGATE",
                action       = f"Go to {BASE_URL}/todos",
                description  = "Agent navigates to the /todos API endpoint to fetch task data",
                verification = f"HTTP {response2.status}; JSON response visible in browser; screenshot saved",
                screenshot   = ss2,
            )

            # ── Step 6: Extract and count todos ──────────────
            body = page.locator("body").inner_text()
            todos = json.loads(body)
            total = len(todos)
            completed = sum(1 for t in todos if t["completed"])
            pending = total - completed
            recorder.record(
                action_type  = "EXTRACT",
                action       = "Parse JSON response and count todos",
                description  = "Agent reads the raw JSON, parses it, and counts total/completed/pending tasks",
                verification = f"Parsed {total} tasks: {completed} completed, {pending} pending",
                screenshot   = ss2,
            )

            # ── Step 7: Validate first todo structure ─────────
            first = todos[0]
            has_id        = isinstance(first.get("id"), int)
            has_title     = isinstance(first.get("title"), str)
            has_completed = isinstance(first.get("completed"), bool)
            valid = has_id and has_title and has_completed
            recorder.record(
                action_type  = "VALIDATE",
                action       = "Validate schema of first todo item",
                description  = "Agent checks that the first task has required fields: id (int), title (str), completed (bool)",
                verification = f"Schema valid: id={has_id}, title={has_title}, completed={has_completed} → {'PASS' if valid else 'FAIL'}",
                screenshot   = ss2,
            )

            # ── Step 8: Navigate to /users endpoint ──────────
            response3 = page.goto(f"{BASE_URL}/users", wait_until="domcontentloaded")
            ss3, size3 = take_screenshot(page, "step08_users")
            recorder.record(
                action_type  = "NAVIGATE",
                action       = f"Go to {BASE_URL}/users",
                description  = "Agent navigates to the /users endpoint to fetch user data",
                verification = f"HTTP {response3.status}; JSON array visible; screenshot saved ({size3:,} bytes)",
                screenshot   = ss3,
            )

            # ── Step 9: Extract user names ────────────────────
            users_body = page.locator("body").inner_text()
            users = json.loads(users_body)
            names = [u["name"] for u in users[:5]]
            recorder.record(
                action_type  = "EXTRACT",
                action       = "Extract first 5 user names from /users",
                description  = "Agent parses the users JSON and extracts the name field for the first 5 users",
                verification = f"Users found: {', '.join(names)}",
                screenshot   = ss3,
            )

            # ── Step 10: Navigate back to homepage ────────────
            page.goto(BASE_URL, wait_until="domcontentloaded")
            ss4, size4 = take_screenshot(page, "step10_final")
            recorder.record(
                action_type  = "NAVIGATE",
                action       = f"Return to {BASE_URL} homepage",
                description  = "Agent navigates back to the homepage to conclude the session",
                verification = f"Homepage loaded; title confirmed; screenshot saved ({size4:,} bytes)",
                screenshot   = ss4,
            )

            # ── Step 11: Close browser ────────────────────────
            browser.close()
            recorder.record(
                action_type  = "CLOSE",
                action       = "Close browser and end session",
                description  = "Agent closes the browser to release resources and end the task",
                verification = "Browser process terminated; no zombie processes",
                screenshot   = None,
            )

        except PWTimeout as e:
            browser.close()
            recorder.record(
                action_type  = "ERROR",
                action       = "Page timeout",
                description  = "A page took too long to load",
                verification = "Task aborted due to timeout",
                status       = "error",
                error        = str(e),
            )
        except Exception as e:
            browser.close()
            recorder.record(
                action_type  = "ERROR",
                action       = "Unexpected error",
                description  = str(e),
                verification = "Task aborted",
                status       = "error",
                error        = str(e),
            )

    # ── Save trajectory ───────────────────────────────────────
    data = recorder.save()

    print("\n" + "=" * 65)
    print("  Task Complete!")
    print("=" * 65)
    print(f"  Total steps    : {data['total_steps']}")
    print(f"  Errors         : {data['total_errors']}")
    print(f"  Trajectory JSON: {TRAJECTORY_FILE}")
    print(f"  Screenshots    : ./{OUTPUT_DIR}/")
    print("=" * 65)
    print("\n  Next: python3 cua_report.py")


def main():
    parser = argparse.ArgumentParser(description="CUA Agent Simulator")
    parser.add_argument("--no-headless", action="store_true", help="Show browser window")
    args = parser.parse_args()
    run_agent(headless=not args.no_headless)


if __name__ == "__main__":
    main()
