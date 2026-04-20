# TODO — meal_planner

> Last synced: 2026-04-20

## Phase 1: Automation & Deployment

- [x] Notion dish database — 60+ Indian dishes with ratings, effort, tags
- [x] Food recommender script (email flow)
- [ ] Schedule cron job for daily automation
- [ ] Keep importing new dishes as they come up

## Phase 2: Security & Stability

- [ ] Remove hardcoded secrets (API keys, email password → .env file)
- [ ] Fix Gmail API token refresh gracefully
- [ ] Add proper error handling and logging

## Phase 3: Smarter Recommendations

- [ ] Improve recommendation scoring algorithm (cuisine diversity, weekly balance, wife preference learning)
- [ ] Add heavy meal / light meal weekly distribution logic
- [ ] Track wife's consistently downvoted dishes

## Phase 4: Expanded Channels

- [ ] Add WhatsApp notification channel (via OpenClaw gateway)

## Phase 5: Dashboard & UX

- [ ] Build meal plan dashboard / manual override UI
- [ ] Auto-generate weekly grocery list

---

## Completed

- [x] Notion dish database (MOS-26)
- [x] Food recommender script — email flow (MOS-27)
