#!/usr/bin/env bash
# ============================================================
# Step 4 — Set up cron to run step3_validate.py every hour
# and log output to /tmp/tasks.log
#
# Usage:
#   chmod +x step4_cron_setup.sh
#   ./step4_cron_setup.sh
#
# To view the cron job after setup:
#   crontab -l
#
# To remove the cron job:
#   crontab -r   (removes ALL jobs) or edit with: crontab -e
# ============================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/step3_validate.py"
LOG_FILE="/tmp/tasks.log"
PYTHON_BIN=$(which python3)

echo "============================================="
echo " Cron Setup: Personal Task Manager"
echo "============================================="
echo " Script     : $PYTHON_SCRIPT"
echo " Python     : $PYTHON_BIN"
echo " Log file   : $LOG_FILE"
echo " Schedule   : Every hour (0 * * * *)"
echo "============================================="

# Check the script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
  echo "Error: $PYTHON_SCRIPT not found."
  echo "Make sure step3_validate.py is in the same directory."
  exit 1
fi

# Build the cron line
CRON_JOB="0 * * * * $PYTHON_BIN $PYTHON_SCRIPT --output $SCRIPT_DIR/validated_tasks.json >> $LOG_FILE 2>&1"

# Check if the cron job already exists
if crontab -l 2>/dev/null | grep -qF "$PYTHON_SCRIPT"; then
  echo ""
  echo "Cron job already exists. No changes made."
  echo "Current crontab entry:"
  crontab -l | grep "$PYTHON_SCRIPT"
else
  # Add the new cron job
  (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
  echo ""
  echo "Cron job added successfully!"
  echo ""
  echo "Entry added:"
  echo "  $CRON_JOB"
fi

echo ""
echo "============================================="
echo " Useful commands:"
echo "   View cron jobs  : crontab -l"
echo "   Edit cron jobs  : crontab -e"
echo "   View log        : tail -f $LOG_FILE"
echo "   Run now (test)  : $PYTHON_BIN $PYTHON_SCRIPT"
echo "============================================="

# ── Optional: Log rotation reminder ──────────────────────────────────────────
echo ""
echo "TIP: To prevent /tmp/tasks.log growing too large, add log rotation."
echo "Create /etc/logrotate.d/tasks with:"
echo ""
echo "  /tmp/tasks.log {"
echo "      daily"
echo "      rotate 7"
echo "      compress"
echo "      missingok"
echo "      notifempty"
echo "  }"
