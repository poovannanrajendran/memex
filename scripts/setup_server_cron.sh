#!/bin/bash

# Safe Cron Setup for memex
PROJECT_DIR="/home/codex_agent_agent/memex"
PYTHON_PATH="$PROJECT_DIR/venv/bin/python3"
SCRIPT_PATH="$PROJECT_DIR/scripts/watcher.py"
LOG_PATH="$PROJECT_DIR/wiki/log.md"

# The new entry
NEW_CRON="18 * * * * cd $PROJECT_DIR && $PYTHON_PATH $SCRIPT_PATH >> $LOG_PATH 2>&1"

# 1. Export current crontab to a temp file
crontab -l > my_cron_backup 2>/dev/null

# 2. Create a new crontab file excluding any EXISTING memex lines
# We use 'scripts/watcher.py' and 'scripts/youtube_watcher.py' as the keys to remove
grep -v "scripts/watcher.py" my_cron_backup | grep -v "scripts/youtube_watcher.py" > my_cron_new

# 3. Append the new entry
echo "$NEW_CRON" >> my_cron_new

# 4. Install the new crontab
crontab my_cron_new

# 5. Clean up
rm my_cron_backup my_cron_new

echo "Cron job updated safely. Existing non-memex jobs were preserved."
