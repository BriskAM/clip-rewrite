#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH="$SCRIPT_DIR/venv/bin/python"
CLEANUP_SCRIPT="$SCRIPT_DIR/cleanup_service.py"

# Check if virtual environment exists
if [ ! -f "$PYTHON_PATH" ]; then
    echo "Error: Virtual environment not found at $SCRIPT_DIR/venv/"
    echo "Please create a virtual environment first."
    exit 1
fi

# Create cron job entry
CRON_COMMAND="0 * * * * cd $SCRIPT_DIR && $PYTHON_PATH $CLEANUP_SCRIPT >> /tmp/clipshare_cleanup.log 2>&1"

echo "Setting up cron job to run cleanup every hour..."
echo "Cron command: $CRON_COMMAND"

# Add to crontab
(crontab -l 2>/dev/null | grep -v "cleanup_service.py"; echo "$CRON_COMMAND") | crontab -

echo "Cron job added successfully!"
echo "Cleanup will run every hour and log to /tmp/clipshare_cleanup.log"
echo ""
echo "To view current cron jobs: crontab -l"
echo "To remove this cron job: crontab -e (then delete the cleanup line)"
echo "To test the cleanup manually: python cleanup_service.py"
