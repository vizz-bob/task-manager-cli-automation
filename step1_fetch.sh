#!/usr/bin/env bash
# ============================================================
# Step 1 — Fetch tasks from JSONPlaceholder API and save to disk
# Usage: ./step1_fetch.sh
# ============================================================
set -euo pipefail

API_URL="https://jsonplaceholder.typicode.com/todos"
OUTPUT_FILE="tasks.json"
LOG_FILE="fetch.log"
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

echo "[$TIMESTAMP] Starting fetch from $API_URL" >> "$LOG_FILE"

# Fetch data from the API
HTTP_STATUS=$(curl --silent --output "$OUTPUT_FILE" \
  --write-out "%{http_code}" \
  --max-time 30 \
  "$API_URL")

if [ "$HTTP_STATUS" -ne 200 ]; then
  echo "[$TIMESTAMP] ERROR: HTTP status $HTTP_STATUS received." >> "$LOG_FILE"
  echo "Error: API returned HTTP $HTTP_STATUS" >&2
  exit 1
fi

# Validate JSON and count records using jq
TASK_COUNT=$(jq '. | length' "$OUTPUT_FILE")
COMPLETED=$(jq '[.[] | select(.completed == true)] | length' "$OUTPUT_FILE")
PENDING=$(jq '[.[] | select(.completed == false)] | length' "$OUTPUT_FILE")

echo "[$TIMESTAMP] SUCCESS: Fetched $TASK_COUNT tasks ($COMPLETED completed, $PENDING pending). Saved to $OUTPUT_FILE" >> "$LOG_FILE"

echo "====================================="
echo " Task Fetch Summary"
echo "====================================="
echo " Timestamp : $TIMESTAMP"
echo " Total     : $TASK_COUNT tasks"
echo " Completed : $COMPLETED"
echo " Pending   : $PENDING"
echo " Saved to  : $OUTPUT_FILE"
echo " Log       : $LOG_FILE"
echo "====================================="
