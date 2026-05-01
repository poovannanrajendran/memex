#!/usr/bin/env bash
set -euo pipefail

# Configuration for automation-runner-01
PROJECT_DIR="/home/labadmin/memex"
VENV_DIR="$PROJECT_DIR/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"
CRON_LOG="/var/log/memex-watcher.log"

echo "Installing memex Automation Engine cron job..."

# Check for Python
if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Error: Python venv not found at $PYTHON_BIN"
  echo "Please ensure the project is cloned and .venv created on the runner."
  exit 1
fi

# Ensure log file exists and is writable
if [[ ! -f "$CRON_LOG" ]]; then
    sudo touch "$CRON_LOG"
    sudo chown labadmin:labadmin "$CRON_LOG"
fi

# Define the cron line: run watcher every 15 minutes
# We cd to the project dir so the python scripts can find each other and .env
CRON_LINE="*/15 * * * * cd $PROJECT_DIR && $PYTHON_BIN scripts/watcher.py >> $CRON_LOG 2>&1"

# Install idempotently (don't duplicate if already there)
( crontab -l 2>/dev/null | grep -v "scripts/watcher.py" ; echo "$CRON_LINE" ) | crontab -

echo "✅ Cron job installed successfully for user labadmin."
echo "Current crontab:"
crontab -l | grep "scripts/watcher.py"
