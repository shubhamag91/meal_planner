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
