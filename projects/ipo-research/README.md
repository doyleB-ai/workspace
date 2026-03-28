---
type: project
status: active
created: 2026-03-26
related: [areas/doyle-config]
---

# IPO Research Agent

## Purpose
Daily research on upcoming IPOs, compiled into a weekly Monday report delivered to John via Telegram.

## Architecture

### Cron Jobs
1. **ipo-daily-research** — Runs daily at 5:00 AM PDT (Sonnet, light context)
   - Searches for upcoming IPOs, S-1 filings, pricing updates, notable news
   - Saves findings to `projects/ipo-research/daily/YYYY-MM-DD.md`
   - No delivery (silent background work)

2. **ipo-monday-report** — Runs Mondays at 6:00 AM PDT (Opus)
   - Reads past 7 days of daily research
   - Compiles concise weekly report
   - Delivers to John via Telegram

### Data Sources (free, no API keys)
- Brave web search (built-in)
- Nasdaq/NYSE IPO calendars
- SEC EDGAR (S-1 filings)
- Financial news sites (Reuters, Bloomberg snippets, Renaissance Capital)

### File Structure
```
projects/ipo-research/
├── README.md          ← this file
├── daily/
│   ├── 2026-03-27.md  ← daily research output
│   ├── 2026-03-28.md
│   └── ...
```

### Follow-up Questions
John can ask Doyle in the main Telegram chat. Doyle reads the daily files and accumulated research to answer.

## Monitoring
- Doyle checks cron run history periodically (via heartbeat or manual)
- Verifies daily files are being created
- Flags if jobs fail or produce empty results

## Cost
- Daily: Sonnet + light context (~low cost per run)
- Monday: Opus for synthesis (~moderate cost, once/week)
