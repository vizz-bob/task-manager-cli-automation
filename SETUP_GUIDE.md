# Personal Task Manager CLI + Web Automation
## Setup & Usage Guide

**Author:** Vijayendra Singh
**API:** https://jsonplaceholder.typicode.com/todos (free, no signup)

---

## Prerequisites

- Linux / macOS terminal
- Python 3.10+
- `bash`, `curl`, `jq` installed
- `pip` / `pip3`

---

## Installation

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Install Playwright browser (for Step 5)
playwright install chromium

# 3. Make bash scripts executable
chmod +x step1_fetch.sh step4_cron_setup.sh
```

---

## Running Each Step

### Step 1 — Fetch tasks from the API (Bash)
```bash
./step1_fetch.sh
# Output: tasks.json, fetch.log
```

### Step 2 — Filter and report tasks (Python)
```bash
python3 step2_filter.py --status all
python3 step2_filter.py --status completed
python3 step2_filter.py --status pending --output pending_tasks.json
```

### Step 3 — Fetch + validate JSON schema (Python)
```bash
python3 step3_validate.py
python3 step3_validate.py --limit 10
python3 step3_validate.py --output my_validated.json
```

### Step 4 — Schedule with cron (runs Step 3 every hour)
```bash
./step4_cron_setup.sh

# Verify cron job was added:
crontab -l

# Watch the log:
tail -f /tmp/tasks.log
```

### Step 5 — Playwright browser automation
```bash
python3 step5_playwright.py
# Output: screenshot_jsonplaceholder.png, step5_results.json

# Show browser window (non-headless):
python3 step5_playwright.py --no-headless
```

---

## Output Files

| File | Created By | Description |
|------|-----------|-------------|
| `tasks.json` | Step 1 | Raw API response (200 tasks) |
| `fetch.log` | Step 1 | Timestamped fetch log |
| `pending_tasks.json` | Step 2 | Filtered pending tasks + metadata |
| `validated_tasks.json` | Step 3 | Schema-validated tasks + error report |
| `screenshot_jsonplaceholder.png` | Step 5 | Full-page browser screenshot |
| `step5_results.json` | Step 5 | Headings, page title, status |

---

## Project File Structure

```
task-manager/
├── step1_fetch.sh              # Bash: curl + jq API fetch
├── step2_filter.py             # Python: filter + report
├── step3_validate.py           # Python: requests + jsonschema
├── step4_cron_setup.sh         # Bash: cron registration
├── step5_playwright.py         # Python: headless browser automation
├── step6_cua_trajectories.md   # CUA trajectory documentation
├── requirements.txt            # Python dependencies
└── SETUP_GUIDE.md              # This file
```

---

## Troubleshooting

**`jq: command not found`**
```bash
# Ubuntu/Debian:
sudo apt-get install jq
# macOS:
brew install jq
```

**`ModuleNotFoundError: requests`**
```bash
pip install requests
```

**Playwright browser not found**
```bash
playwright install chromium
```

**Cron job not running**
```bash
# Check cron service is running:
sudo service cron status   # Linux
# Or check system logs:
grep CRON /var/log/syslog
```
