#!/usr/bin/env bash
set -euo pipefail

# Configuration
PROJECT_DIR="/home/labadmin/memex"
VENV_DIR="$PROJECT_DIR/.venv"
PYTHON_BIN="$VENV_DIR/bin/python"
CRON_LOG="/var/log/memex-watcher.log"

# Check for Python
if [[ ! -x "$PYTHON_BIN" ]]; then
  echo "Error: Python venv not found at $PYTHON_BIN"
  echo "Please ensure the project is cloned and .venv created at $PROJECT_DIR"
  exit 1
fi

# Ensure log directory exists (might need sudo if not writable by user)
if [[ ! -d "/var/log" ]]; then
    sudo mkdir -p /var/log
fi
sudo touch "$CRON_LOG"
sudo chown labadmin:labadmin "$CRON_LOG"

# Define the cron line: run watcher every 15 minutes
CRON_LINE="*/15 * * * * cd $PROJECT_DIR && $PYTHON_BIN scripts/watcher.py >> $CRON_LOG 2>&1"

# Install idempotently
( crontab -l 2>/dev/null | grep -v "scripts/watcher.py" ; echo "$CRON_LINE" ) | crontab -

echo "✅ Cron job installed successfully."
crontab -l | grep "scripts/watcher.py"
