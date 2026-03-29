# Fiduciary Advisory Board

Multi-agent system operating as a team of fiduciary financial advisors for John.

## Status
**Building** — All agent prompts complete. Weekly cron configured. Awaiting portfolio data from John.

## Team

| Agent | Role | Model |
|-------|------|-------|
| Chief Financial Advisor (CFA) | Primary interface, orchestrator, synthesizer | Opus/Sonnet |
| Investment Analyst | Portfolio analysis, allocation, benchmarking | Sonnet |
| Real Estate Analyst | Property valuation, mortgage optimization | Sonnet |
| Retirement Strategist | Timeline modeling, withdrawal strategy | Sonnet |
| Tax Strategist | Tax efficiency, harvesting, asset location | Sonnet |
| Market Research Analyst | On-demand deep equity/market research | Sonnet (via Claude Code) |

**Not included (by John's request):** Insurance & Risk Specialist

## Architecture

Hub-and-spoke. CFA is the hub, specialists are spokes.

```
         John
           │
           ▼
    ┌──────────────┐
    │     CFA      │
    └──────┬───────┘
     ┌─────┼─────┬──────┐
     ▼     ▼     ▼      ▼
   Invest Real  Retire  Tax
   Analyst Estate Strat  Strat
```

## Cadence

- **Weekly** scheduled analysis + report delivery via Telegram
- **On-demand** sessions when John wants to discuss something

## Market Research Agent (On-Demand)

Triggered via Doyle when John asks for research on a specific company, sector, or theme.
- Runs as Claude Code with shell access (Python venv with financial libraries)
- Uses yfinance, SEC EDGAR, web search for data gathering
- Produces institutional-quality research reports
- Reports saved to `research/reports/[TICKER]-[YYYY-MM-DD].md`
- Python venv: `research/tools/venv/`
- Approved packages: yfinance, pandas, numpy, matplotlib, requests, beautifulsoup4, lxml

## Data Input

John will provide portfolio data via attached files or Google Sheets.
Data will be parsed into structured files in `portfolio/`.
⚠️ **All account numbers, routing numbers, and SSNs must be redacted before storage.**
Use labels (e.g., "Fidelity Roth", "Schwab Brokerage") instead.

## Data Storage

```
portfolio/
├── holdings.md        ← stocks, bonds, funds, crypto
├── real-estate.md     ← properties, mortgages, equity
├── retirement.md      ← 401k, IRA, Roth, targets
└── tax-profile.md     ← filing status, brackets, considerations
```

## Agent Prompts

```
agents/
├── cfa.md
├── investment.md
├── real-estate.md
├── retirement.md
└── tax.md
```

## Reports

Weekly reports archived in `reports/weekly/YYYY-MM-DD.md`

## Next Steps

1. [x] Write agent system prompts (completed 2026-03-28)
2. [ ] John provides portfolio data (from laptop, no rush)
3. [ ] Parse and structure data into portfolio/ files
4. [ ] John reviews structured data for accuracy
5. [x] Configure cron jobs for weekly cycle (completed 2026-03-28, job ID: 46437dc7-e3bf-412d-ba41-49da167f4dd8)
6. [ ] First test run (scheduled for 2026-03-30, 9 AM PT)
7. [ ] Go live

## Decisions Log

- 2026-03-27: Architecture defined. All specialists except Insurance. Weekly cadence. No cost ceiling.
- 2026-03-27: John will gather data from laptop another day. Building scaffolding in advance.
- 2026-03-28: All 5 agent prompts (CFA, Investment, Real Estate, Retirement, Tax) completed and tested.
- 2026-03-28: Weekly briefing cron job configured (Sundays 9:00 AM PT, announces to Telegram). First test run queued for 2026-03-30.
- 2026-03-28: Market research agent (on-demand) architecture finalized. Python venv with yfinance/pandas/numpy. Security: approved packages + domains only. First AMZN report: STRONG HOLD rating, noted FTC risk (Oct 2026 trial), FCF collapse risk, recommend RSU diversification given 41% concentration.
- 2026-03-28: Reviewed superpowers framework (obra/superpowers) — not suitable for research agent (dev workflow tool, not research-oriented). Proceeded with custom Python + web search architecture.
