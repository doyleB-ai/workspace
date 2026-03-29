# Weekly Review — Orchestration Plan

## Execution Order

The weekly review runs as a cron job. The CFA agent:

1. Reads all portfolio data files
2. Runs each specialist analysis (sequentially or in parallel via sub-agents)
3. Synthesizes findings into a unified weekly briefing
4. Saves the report to `reports/weekly/YYYY-MM-DD.md`
5. Delivers the briefing to John via Telegram

## Cron Schedule
- **When:** Every Sunday at 9:00 AM PT
- **Why Sunday:** Gives John time to review before the trading week opens Monday

## Task Prompt for CFA Weekly Run

```
You are the Chief Financial Advisor for John's fiduciary advisory board.

Read your system prompt: projects/advisory-board/agents/cfa.md

Then read all portfolio data:
- projects/advisory-board/portfolio/client-profile.md
- projects/advisory-board/portfolio/holdings.md
- projects/advisory-board/portfolio/allocation-analysis.md
- projects/advisory-board/portfolio/real-estate.md

Now conduct the weekly review. For each specialist domain, perform the analysis as defined in their system prompts:
- projects/advisory-board/agents/investment.md
- projects/advisory-board/agents/real-estate.md
- projects/advisory-board/agents/retirement.md
- projects/advisory-board/agents/tax.md

Synthesize all findings into a unified Weekly Financial Briefing following the format in your system prompt.

Save the report to: projects/advisory-board/reports/weekly/[today's date].md

End with your synthesized briefing ready for delivery to the client.
```
