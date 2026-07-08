# meal_planner

Personal Indian meal planning system. Manages a Notion database of 60+ dishes, scores them intelligently, sends daily plans to wife via email, reads replies, and updates Notion.

---

## Quick Start

```bash
cd ~/Projects/meal_planner/code
pip install requests google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Set env vars (create .env file or export)
export NOTION_API_KEY="your_notion_key"
export DATABASE_ID="your_notion_database_id"
export EMAIL_PASSWORD="your_gmail_app_password"
export SENDER_EMAIL="your_gmail_address"
export WIFE_EMAIL="recipient_email"

# Run manually
python food_recommender.py

# Or set up automated daily execution (see below)
```

---

## Automated Execution (Cron Job)

The system can be configured to run automatically every day using the provided setup script:

```bash
# From the project root directory:
./setup_cron.sh
```

This will:
- Create a cron job to run the meal planner at 7:00 AM daily
- Set up logging to `logs/meal_planner_cron.log`
- Source your `.env` file for environment variables if it exists

To view logs:
```bash
tail -f logs/meal_planner_cron.log
```

To modify the cron job:
```bash
crontab -e
```

To remove the cron job:
```bash
crontab -r
```

**Note**: Make sure your `.env` file is properly configured with:
```
NOTION_API_KEY=your_notion_key
DATABASE_ID=your_database_id
EMAIL_PASSWORD=your_email_password
SENDER_EMAIL=your_email@gmail.com
WIFE_EMAIL=recipient@email.com
```

---

## Project Structure

```
code/
  food_db.py           # Dish database schema
  food_recommender.py  # Main automation script

data/
  today_options.json    # Last generated meal plan

docs/
  project-overview.md   # Full project documentation
  setup-overview.md     # Local tool setup

TODO.md                # Task tracker
README.md              # This file
```

---

## Current Issues

See Linear: https://linear.app/mose/project/meal-planner-b9cf6d580a24
