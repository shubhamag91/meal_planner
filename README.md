# meal_planner

Personal Indian meal planning system. Manages a Notion database of 60+ dishes, scores them intelligently (with cuisine-variety and seasonal adjustments), sends daily plans to wife via email, reads replies, and updates Notion.

Requires Python 3.

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
python3 food_recommender.py

# Or set up automated daily execution (see below)
```

**Never hardcode these values in source** — always use `.env` / environment variables. This project's git history previously had a hardcoded Notion token and Gmail app password committed; both were scrubbed from git history on 2026-07-08. If you're the original owner of that Notion token / Gmail app password and haven't rotated them yet, treat them as compromised and do so before relying on this project again. See `.env.example` for the expected variable names.

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

## Testing

A handful of standalone Python 3 scripts check the code without hitting real APIs or sending real email/Notion writes:

```bash
python3 simple_test.py          # imports resolve, cron script is present & executable
python3 test_core_logic.py      # file structure, no hardcoded secrets, README/cron content
python3 test_cron.py            # env var loading, should_send_today(), file logging
python3 test_scoring.py         # scoring functions imported from code/food_recommender.py
python3 test_scoring_logic.py   # scoring functions re-implemented inline, tested in isolation
```

None of these require `.env` to be set, and none send email, write to Notion, or make network calls. Run them from the project root.

---

## Project Structure

```
code/
  food_db.py           # Dish database schema + one-off Notion bulk-upload (run directly, not imported)
  food_recommender.py  # Main automation script — scoring, email, Gmail reply parsing, Notion updates

data/
  today_options.json    # Snapshot of a past run's options (see note below)

docs/
  project-overview.md   # Full project documentation

TODO.md                # Task tracker
README.md              # This file
setup_cron.sh           # Installs the daily cron job
simple_test.py, test_*.py  # Standalone tests (see Testing section above)
```

**Note**: `save_today_options()` in `food_recommender.py` writes `today_options.json` to the current working directory at runtime, not literally to `data/`. When run via `setup_cron.sh` (which `cd`s to the project root first), the file lands in the project root, not in `data/`.

---

## Current Issues

See Linear: https://linear.app/mose/project/meal-planner-b9cf6d580a24
