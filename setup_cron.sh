#!/bin/bash
# Setup script for cron automation of meal planner

# Configuration
PROJECT_DIR="/Users/shubham/Projects/meal_planner"
LOG_DIR="$PROJECT_DIR/logs"
CRON_TIME="0 7 * * *"  # 7:00 AM daily
PYTHON_SCRIPT="$PROJECT_DIR/code/food_recommender.py"
LOG_FILE="$LOG_DIR/meal_planner_cron.log"
ENV_FILE="$PROJECT_DIR/.env"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Check if .env file exists
ENV_SOURCE=""
if [ -f "$ENV_FILE" ]; then
    ENV_SOURCE="source $ENV_FILE &&"
    echo "Found .env file, will source it in cron job"
else
    echo "Warning: No .env file found at $ENV_FILE"
    echo "Make sure to set required environment variables:"
    echo "  NOTION_API_KEY, DATABASE_ID, EMAIL_PASSWORD, SENDER_EMAIL, WIFE_EMAIL"
fi

# Create the cron job command
# Using bash -c to ensure proper environment and sourcing
CRON_CMD="$CRON_TIME cd $PROJECT_DIR && bash -c \"$ENV_SOURCE /usr/bin/python3 $PYTHON_SCRIPT\" >> $LOG_FILE 2>&1"

# Install the cron job
(
  # List existing cron jobs
  crontab -l 2>/dev/null
  # Add new cron job
  echo "$CRON_CMD"
) | crontab -

echo "Cron job installed successfully!"
echo "Schedule: $CRON_TIME"
echo "Command: cd $PROJECT_DIR && bash -c \"$ENV_SOURCE /usr/bin/python3 $PYTHON_SCRIPT\""
echo "Log file: $LOG_FILE"
echo ""
echo "To view logs: tail -f $LOG_FILE"
echo "To edit cron job: crontab -e"
echo "To remove cron job: crontab -r"
echo ""
echo "IMPORTANT: Make sure your .env file is properly configured with:"
echo "  NOTION_API_KEY=your_notion_key"
echo "  DATABASE_ID=your_database_id"
echo "  EMAIL_PASSWORD=your_email_password"
echo "  SENDER_EMAIL=your_email@gmail.com"
echo "  WIFE_EMAIL=recipient@email.com"