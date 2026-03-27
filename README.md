# Personal Task Manager CLI + Web Automation

A command-line pipeline that fetches tasks from a public REST API, validates JSON schema, filters and saves results, schedules automatic runs via cron, and automates browser interaction using Playwright — all documented as CUA trajectories.

> Built to demonstrate skills for Computer-Use Agent (CUA) annotation roles.

---

## Project Structure

```
.
├── step1_fetch.sh              # Bash: fetch tasks via curl + jq
├── step2_filter.py             # Python: filter + report tasks
├── step3_validate.py           # Python: requests + jsonschema validation
├── step4_cron_setup.sh         # Bash: cron job registration
├── step5_playwright.py         # Python: headless browser automation
├── step6_cua_trajectories.md   # CUA trajectory documentation
├── Dockerfile                  # Docker environment
├── docker-compose.yml          # Container orchestration
├── docker_run.sh               # Helper script
├── requirements.txt            # Python dependencies
└── SETUP_GUIDE.md              # Full setup instructions
```

---

## Quick Start (Docker)

```bash
chmod +x docker_run.sh
./docker_run.sh build    # Build image (~2 min first time)
./docker_run.sh start    # Start container
./docker_run.sh shell    # Open bash inside container
```

Inside the container:

```bash
./step1_fetch.sh                                        # Step 1
python3 step2_filter.py --status pending                # Step 2
python3 step3_validate.py                               # Step 3
./step4_cron_setup.sh                                   # Step 4
python3 step5_playwright.py                             # Step 5
```

---

## What Each Step Does

### Step 1 — Bash: Fetch & Save
- Calls `https://jsonplaceholder.typicode.com/todos` with `curl`
- Validates response with `jq`, counts tasks
- Logs result with timestamp to `fetch.log`
- Practices: `curl`, `jq`, `set -euo pipefail`, file redirection

### Step 2 — Python: Filter & Report
- Reads `tasks.json`, filters by `completed` / `pending` / `all`
- Prints grouped summary by userId
- Saves filtered report as JSON with metadata
- Practices: `argparse`, `json`, `os`, file I/O

### Step 3 — Python: API + Schema Validation
- Fetches tasks directly using `requests`
- Validates every record: `id` (int), `userId` (int), `title` (str), `completed` (bool)
- Collects validation errors without crashing
- Practices: `requests`, `jsonschema`, HTTP error handling

**Sample output:**
```
Total records  : 200
Valid          : 200
Invalid        : 0
All records passed schema validation.
Completed tasks : 90  |  Pending tasks : 110
```

### Step 4 — Bash + Cron: Scheduling
- Registers `step3_validate.py` to run every hour via `crontab`
- Logs all output to `/tmp/tasks.log`
- Prevents duplicate entries on re-run
- Practices: `cron`, log rotation guidance

### Step 5 — Playwright: Browser Automation
- Launches headless Chromium via Playwright
- Navigates to `https://jsonplaceholder.typicode.com`
- Extracts all `h1`/`h2`/`h3` headings
- Takes a full-page screenshot
- Saves results to `step5_results.json`

**Sample output:**
```
Page title: JSONPlaceholder - Free Fake REST API
<h1>: JSONPlaceholder
<h1>: Free fake and reliable API for testing and prototyping.
<h2>: Sponsors  |  Try it  |  When to use  |  Resources ...
Status: SUCCESS  |  Screenshot saved (311,328 bytes)
```

### Step 6 — CUA Trajectory Documentation
Full trajectory tables for all 5 steps — each action documented with description and verification method. See [`step6_cua_trajectories.md`](step6_cua_trajectories.md).

---

## Skills Demonstrated

| Skill | Covered By |
|-------|-----------|
| Linux CLI | Steps 1, 4 |
| Bash scripting | Steps 1, 4 |
| Python scripting | Steps 2, 3, 5 |
| REST APIs | Steps 1, 3 |
| JSON + schema validation | Steps 2, 3 |
| File I/O | Steps 1, 2, 3, 5 |
| Browser automation | Step 5 |
| CUA trajectory writing | Step 6 |
| Cron / scheduling | Step 4 |
| Docker / containerisation | Dockerfile |

---

## API Used

[JSONPlaceholder](https://jsonplaceholder.typicode.com) — free, public, no signup required.

```
GET https://jsonplaceholder.typicode.com/todos
```
Returns 200 task objects with `id`, `userId`, `title`, and `completed` fields.

---

## Requirements

- Docker (recommended), or Python 3.10+ + bash + curl + jq
- See `SETUP_GUIDE.md` for full instructions

---

## Author

Vijayendra Singh
