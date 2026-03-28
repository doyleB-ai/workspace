# Fiduciary Advisory Board

Multi-agent system operating as a team of fiduciary financial advisors for John.

## Status
**Building** — Architecture defined, awaiting portfolio data from John.

## Team

| Agent | Role | Model |
|-------|------|-------|
| Chief Financial Advisor (CFA) | Primary interface, orchestrator, synthesizer | Opus/Sonnet |
| Investment Analyst | Portfolio analysis, allocation, benchmarking | Sonnet |
| Real Estate Analyst | Property valuation, mortgage optimization | Sonnet |
| Retirement Strategist | Timeline modeling, withdrawal strategy | Sonnet |
| Tax Strategist | Tax efficiency, harvesting, asset location | Sonnet |

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

1. [ ] Write agent system prompts
2. [ ] John provides portfolio data (from laptop, no rush)
3. [ ] Parse and structure data into portfolio/ files
4. [ ] John reviews structured data for accuracy
5. [ ] Configure cron jobs for weekly cycle
6. [ ] First test run
7. [ ] Go live

## Decisions Log

- 2026-03-27: Architecture defined. All specialists except Insurance. Weekly cadence. No cost ceiling.
- 2026-03-27: John will gather data from laptop another day. Building scaffolding in advance.
