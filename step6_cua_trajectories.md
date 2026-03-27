# Step 6 — CUA Trajectory Documentation

**Project:** Personal Task Manager CLI + Web Automation
**Author:** Vijayendra Singh
**Date:** 2026-03-27

---

## What is a CUA Trajectory?

A CUA (Computer-Use Agent) trajectory is a structured record of:
- The **action** an agent takes
- A clear **description** of what that action does
- A **verification** step that confirms the action succeeded

Trajectories are used to annotate agent behaviour for AI training datasets.

---

## Step 1 — Bash Script: Fetch and Save API Data

**Script:** `step1_fetch.sh`
**Goal:** Call the JSONPlaceholder REST API and save tasks to `tasks.json`

| # | Action | Description | Verification |
|---|--------|-------------|--------------|
| 1 | `chmod +x step1_fetch.sh` | Makes the bash script executable by the current user | Run `ls -la step1_fetch.sh` — confirm `-rwxr-xr-x` permissions |
| 2 | `./step1_fetch.sh` | Executes the script; triggers `curl` to fetch from `https://jsonplaceholder.typicode.com/todos` | Terminal prints a summary table with task count |
| 3 | `curl` sends HTTP GET | Makes the network request; writes raw JSON body to `tasks.json`; captures HTTP status code | Check `$HTTP_STATUS -eq 200`; script exits with error if not |
| 4 | `jq '. \| length'` | Counts total records in the returned JSON array | Output shows "Total: 200 tasks" (expected count from this API) |
| 5 | `echo "..." >> fetch.log` | Appends a timestamped entry to `fetch.log` | Run `cat fetch.log` — entry shows `[YYYY-MM-DD HH:MM:SS] SUCCESS` |
| 6 | Inspect `tasks.json` | Verify file was written and is valid JSON | Run `jq '.[0]'` — prints first task with `id`, `userId`, `title`, `completed` |

---

## Step 2 — Python: Read, Filter, and Update Tasks

**Script:** `step2_filter.py`
**Goal:** Load `tasks.json`, filter by status, print summary, save report

| # | Action | Description | Verification |
|---|--------|-------------|--------------|
| 1 | `python3 step2_filter.py --status all` | Loads `tasks.json` and displays all 200 tasks grouped by userId | Terminal shows table with 200 total, split by user |
| 2 | `python3 step2_filter.py --status completed` | Filters tasks where `completed == true` | Only completed tasks appear; count matches `jq '[.[] \| select(.completed)] \| length' tasks.json` |
| 3 | `python3 step2_filter.py --status pending` | Filters tasks where `completed == false` | Only pending tasks appear |
| 4 | `python3 step2_filter.py --status pending --output pending_tasks.json` | Saves filtered results to `pending_tasks.json` with metadata | Run `jq '.filter, .total_count' pending_tasks.json` — returns `"pending"` and correct count |
| 5 | File I/O: `open(filepath, "r")` | Reads tasks from disk; raises `FileNotFoundError` if missing | Script exits with helpful message "Run step1_fetch.sh first" if file absent |
| 6 | File I/O: `open(output_path, "w")` | Writes filtered report to output file | Confirm file exists: `ls -lh pending_tasks.json` |

---

## Step 3 — Python: API Fetch with JSON Schema Validation

**Script:** `step3_validate.py`
**Goal:** Fetch tasks directly via `requests`, validate each record against a schema

| # | Action | Description | Verification |
|---|--------|-------------|--------------|
| 1 | `python3 step3_validate.py` | Starts script; imports `requests` and `jsonschema` (exits with install hint if missing) | No ImportError; script proceeds to fetch step |
| 2 | `requests.get(API_URL, timeout=30)` | Makes HTTP GET to the API with a 30-second timeout | Response status code printed: `Status: 200 OK` |
| 3 | `response.raise_for_status()` | Raises `HTTPError` for 4xx or 5xx responses | No exception raised for 200 response |
| 4 | `validate(instance=task, schema=TASK_SCHEMA)` | Validates each task has `id` (int), `userId` (int), `title` (string), `completed` (bool) | Report shows "All 200 records passed schema validation" |
| 5 | Error collection loop | Any invalid record is caught with `ValidationError` and added to `errors` list (not raised) | Validation report shows `Invalid: 0` for clean API data |
| 6 | Save to `validated_tasks.json` | Writes valid tasks + metadata + any errors to JSON file | `jq '.total_valid, .total_errors' validated_tasks.json` returns `200` and `0` |
| 7 | `--limit 10` flag | Restricts processing to first N tasks for quick testing | Run `python3 step3_validate.py --limit 10`; output shows "Total: 10" |

---

## Step 4 — Bash + Cron: Schedule Automation

**Script:** `step4_cron_setup.sh`
**Goal:** Register a cron job to run `step3_validate.py` every hour

| # | Action | Description | Verification |
|---|--------|-------------|--------------|
| 1 | `chmod +x step4_cron_setup.sh` | Makes the setup script executable | `ls -la step4_cron_setup.sh` shows execute bit set |
| 2 | `./step4_cron_setup.sh` | Script checks for `step3_validate.py`, then reads existing crontab with `crontab -l` | Script prints current working directory and Python binary path |
| 3 | Guard: `if crontab -l \| grep -qF "$PYTHON_SCRIPT"` | Prevents duplicate cron entries if run more than once | Re-running script prints "Cron job already exists. No changes made." |
| 4 | `(crontab -l; echo "$CRON_JOB") \| crontab -` | Appends the new `0 * * * *` entry to the user's crontab | `crontab -l` shows the new line ending with `>> /tmp/tasks.log 2>&1` |
| 5 | Cron fires at `0 * * * *` | System runs `python3 step3_validate.py` at the top of every hour | Wait for next hour; check `tail /tmp/tasks.log` for new timestamp entry |
| 6 | `tail -f /tmp/tasks.log` | Follow the log file in real time | New lines appear each hour with fetched/validated task counts |

---

## Step 5 — Playwright: Browser Automation

**Script:** `step5_playwright.py`
**Goal:** Open the site headlessly, extract headings, take a screenshot

| # | Action | Description | Verification |
|---|--------|-------------|--------------|
| 1 | `pip install playwright && playwright install chromium` | Installs Playwright library and downloads the Chromium browser binary | `python3 -c "from playwright.sync_api import sync_playwright"` succeeds without error |
| 2 | `python3 step5_playwright.py` | Launches script; creates a Playwright `sync_playwright()` context | Script prints "Navigating to https://jsonplaceholder.typicode.com ..." |
| 3 | `browser = p.chromium.launch(headless=True)` | Opens a headless Chromium instance (no visible window) | No browser window appears on screen |
| 4 | `page.goto(TARGET_URL, wait_until="domcontentloaded")` | Navigates to the URL; waits for DOM to finish loading | Console shows `HTTP Status: 200` |
| 5 | `page.wait_for_selector("h1, h2, h3")` | Waits until at least one heading element is present in DOM | No `TimeoutError` raised; script continues |
| 6 | `page.locator("h1").all()` + `el.inner_text()` | Iterates all `h1`, `h2`, `h3` elements and collects visible text | Console prints heading text, e.g. `<h1>: JSONPlaceholder` |
| 7 | `page.screenshot(path=..., full_page=True)` | Captures a full-page PNG screenshot | File `screenshot_jsonplaceholder.png` is created; `ls -lh` shows non-zero size |
| 8 | JSON results saved to `step5_results.json` | Writes page title, headings, timestamp, screenshot path, and status to JSON | `jq '.status' step5_results.json` returns `"success"` |
| 9 | `browser.close()` | Closes the browser and frees resources | No zombie `chromium` processes in `ps aux` output |

---

## Summary: Skills Demonstrated

| Skill | Covered By |
|-------|-----------|
| Linux CLI | Steps 1, 4 |
| Bash scripting | Steps 1, 4 |
| Python scripting | Steps 2, 3, 5 |
| REST APIs | Steps 1, 3 |
| JSON + schema validation | Steps 2, 3 |
| File operations | Steps 1, 2, 3, 5 |
| Browser automation | Step 5 |
| CUA trajectory writing | Step 6 (this document) |
| Cron / scheduling | Step 4 |

---

## Interview Talking Point

> "I built a personal project to practice all the core skills for this role. I created a CLI pipeline that fetches tasks from a REST API, validates the JSON schema, filters and saves results using Python, and schedules automatic runs via cron. I also wrote a Playwright script to automate a browser check and capture screenshot evidence. Finally I documented every workflow as a CUA trajectory with explicit verification steps — which is exactly the annotation discipline I'd apply in this role."
