# meal_planner — Project Overview

> Document created: 2026-04-20
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
│   ├── food_db.py          # Notion database schema and dish definitions
│   ├── food_recommender.py # Main script — scores, emails, reads replies
│   └── today_options.json   # Output of last run (auto-generated)
├── data/                   # Meal history, logs, output files
├── docs/                   # Project documentation
├── articles/               # Recipe references, diet guides
├── links/                  # Useful URLs
├── notes/                  # Meeting notes, decisions
├── prompts/                # Prompts used for this project
├── archive/                # Old versions of scripts
├── inbox/                  # Incoming ideas / unsorted tasks
├── outputs/                # Generated reports
└── tmp/                    # Temporary working files
```

---

## Current Status

### ✅ Working
- Notion database of 60+ dishes (Breakfast, Lunch, Dinner)
- Scoring algorithm (freshness + ratings - effort penalty)
- Daily email to wife with meal suggestions
- Email reply parsing (B1 L2 D3 format)
- Notion "Last Eaten" auto-update

### ⚠️ Issues to Fix
- API keys and email password hardcoded in `food_recommender.py`
- No cron job — requires manual run
- Gmail API token refresh fix needed

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Dish database | Notion API |
| Notification | Email (Gmail SMTP) |
| Reply handling | Gmail API |
| Scheduling | Manual (cron to be added) |
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
