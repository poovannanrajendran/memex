#!/bin/bash

# Absolute paths
PYTHON_PATH="/opt/anaconda3/bin/python"
PROJECT_DIR="/Users/poovannanrajendran/Documents/GitHub/memex"
SCRIPT_PATH="$PROJECT_DIR/scripts/youtube_watcher.py"
LOG_PATH="$PROJECT_DIR/wiki/log.md"

# Cron entry: 18 minutes past every hour
CRON_ENTRY="18 * * * * cd $PROJECT_DIR && $PYTHON_PATH $SCRIPT_PATH 5 >> $LOG_PATH 2>&1"

# Check if entry already exists
(crontab -l 2>/dev/null | grep -F "$SCRIPT_PATH") && echo "Cron job already exists." && exit 0

# Add to crontab
(crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -

echo "Cron job scheduled: 18 minutes past every hour."
echo "Entry: $CRON_ENTRY"
