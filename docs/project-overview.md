# meal_planner — Project Overview

> Document created: 2026-04-20
> Last updated: 2026-07-08
> Author: OpenClaw agent (assisted by Shubham)

---

## What it is

A personal meal planning system that:
- Pulls ~60+ Indian dishes from a Notion database
- Scores each dish by freshness, ratings (yours + wife's), and effort
- Sends a daily meal plan email to wife (rudrakshharlalka@gmail.com)
- Reads wife's B1/L2/D3 reply from email
- Updates "Last Eaten" date in Notion

---

## Project Structure

```
meal_planner/
├── code/
│   ├── food_db.py          # Notion database schema, dish definitions, one-off bulk-upload (run directly)
│   └── food_recommender.py # Main script — scores, emails, reads replies, updates Notion
├── data/                   # Meal history, logs, output files
├── docs/                   # Project documentation
├── articles/               # Recipe references, diet guides
├── links/                  # Useful URLs
├── notes/                  # Meeting notes, decisions
├── prompts/                # Prompts used for this project
├── archive/                # Old versions of scripts
├── inbox/                  # Incoming ideas / unsorted tasks
├── outputs/                # Generated reports
├── tmp/                    # Temporary working files
├── setup_cron.sh           # Installs the daily cron job
└── simple_test.py, test_*.py  # Standalone Python 3 tests, no network/credentials required
```

`today_options.json` is written by `save_today_options()` to the process's current working directory at runtime — not reliably to `code/` or `data/`. When run via `setup_cron.sh` it lands in the project root.

---

## Current Status

### ✅ Working
- Notion database of 60+ dishes (Breakfast, Lunch, Dinner)
- Scoring algorithm: base freshness + ratings - effort penalty, plus a cuisine-variety penalty (`get_recent_cuisine_penalty`) and a seasonal boost (`get_seasonal_boost`)
- Daily email to wife with meal suggestions, with retry/backoff on send failures
- Email reply parsing (B1 L2 D3 format)
- Notion "Last Eaten" auto-update, with retry/backoff on the Notion API calls
- Cron automation via `setup_cron.sh` (7:00 AM daily)
- Basic kitchen-tablet dashboard (`send_smart_display()` writes `meal_plan_dashboard.html`)
- Python 3 test suite (`simple_test.py`, `test_core_logic.py`, `test_cron.py`, `test_scoring.py`, `test_scoring_logic.py`) — all pass, no credentials or network required

### ⚠️ Issues to Fix
- Gmail API token refresh fix needed
- WhatsApp notification channel is a placeholder (`send_whatsapp()`) — no real Twilio integration yet
- `today_options.json` save path is inconsistent — writes to cwd rather than a fixed `data/` location
- No weekly heavy/light meal balance or wife-preference-learning logic yet

### 🔒 Security note
A hardcoded Notion API token and Gmail app password were found in the earliest git commits (`code/food_db.py` and `code/food_recommender.py`). Both were removed from all git history via `git filter-repo` on 2026-07-08. If those credentials haven't been rotated since, treat them as compromised.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Dish database | Notion API |
| Notification | Email (Gmail SMTP), with WhatsApp and a local HTML dashboard as additional/stubbed channels |
| Reply handling | Gmail API |
| Scheduling | cron (`setup_cron.sh`), 7:00 AM daily |
| Project tracking | Linear (meal_planner project) |

---

## Linear Project

**URL:** https://linear.app/mose/project/meal-planner-b9cf6d580a24

| Phase | Description |
|-------|-------------|
| Phase 1 | Automation & Deployment |
| Phase 2 | Security & Stability |
| Phase 3 | Smarter Recommendations |
| Phase 4 | Expanded Channels |
| Phase 5 | Dashboard & UX |
