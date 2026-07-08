# TODO — meal_planner

> Last synced: 2026-07-08

## Phase 1: Automation & Deployment

- [x] Notion dish database — 60+ Indian dishes with ratings, effort, tags
- [x] Food recommender script (email flow)
- [x] Schedule cron job for daily automation (`setup_cron.sh`)
- [ ] Keep importing new dishes as they come up
- [ ] Fix `today_options.json` save path — currently written to the process's cwd, not consistently to `data/` (see README note)

## Phase 2: Security & Stability

- [x] Remove hardcoded secrets (API keys, email password → .env file) — code uses `os.environ.get`, and a hardcoded Notion token + Gmail app password found in early git history were scrubbed from all commits on 2026-07-08
- [ ] Rotate the exposed Notion API token and Gmail app password (if not already done) — treat as compromised since they lived in local git history
- [ ] Fix Gmail API token refresh gracefully
- [x] Add retry/backoff for Notion API calls and email sending (`setup_session_with_retries`, exponential backoff on send_email)
- [x] Fix silent bugs found while testing: `datetime` shadowing crash in `get_recent_cuisine_penalty`, duplicate `log()` definition that disabled file logging, and `food_db.py` firing live Notion requests on mere import

## Phase 3: Smarter Recommendations

- [x] Cuisine variety penalty (`get_recent_cuisine_penalty`) and seasonal boost (`get_seasonal_boost`) added to scoring
- [ ] Weekly heavy/light meal balance logic beyond the existing lunch→dinner heuristic
- [ ] Wife preference learning / track consistently downvoted dishes

## Phase 4: Expanded Channels

- [ ] Add WhatsApp notification channel — `send_whatsapp()` exists as a placeholder only; needs real Twilio integration

## Phase 5: Dashboard & UX

- [x] Basic meal plan dashboard — `send_smart_display()` writes `meal_plan_dashboard.html` for a kitchen tablet
- [ ] Manual override UI (dashboard is currently read-only, auto-refreshing)
- [ ] Auto-generate weekly grocery list

---

## Completed

- [x] Notion dish database (MOS-26)
- [x] Food recommender script — email flow (MOS-27)
- [x] Cron automation, cuisine/seasonal scoring, multi-channel notification stubs, retry logic, Python 3 test suite, and secret scrubbing from git history (2026-07-08)
