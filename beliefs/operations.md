---
subject: operational-patterns
type: belief
last_updated: 2026-03-21
related: [facts/infrastructure]
---

# Operational Patterns

## [observation] API credit depletion causes cascading failure
- first_observed: 2026-03-18
- evidence: Ran out of API credits on 2026-03-18. After adding credits, Doyle stayed unresponsive/erroring. Required full reboot + `openclaw doctor` to recover. Root cause: session/gateway caches auth failure state even after credits restored.
- confidence: low — single incident, but severe enough to note

## [belief] Switching to subscription auth prevents credit-related outages
- first_observed: 2026-03-18
- upgraded: 2026-03-19
- evidence: The 2026-03-18 outage was caused by API credit depletion. Switched to subscription auth on 2026-03-19. No more credit balance to deplete.
- confidence: high — migration complete

## [belief] Cron jobs get calendar entries
- first_observed: 2026-03-19
- evidence: John explicitly requested — "Any cron should have a calendar that I can reference."
- confidence: high
- rule: When creating cron jobs, also add corresponding Google Calendar event(s) so John has visibility into scheduled automation.
- note: Heartbeats don't need calendar entries (too frequent, background polling).

## [belief] Cron jobs use Sonnet by default
- first_observed: 2026-03-19
- evidence: John requested Sonnet for cron jobs (cheaper/faster for automated tasks), Opus for interactive chat.
- confidence: high
- rule: When creating cron jobs, always specify `--model anthropic/claude-sonnet-4-6`

## [observation] Auth failures cause silent unresponsiveness
- first_observed: 2026-03-21
- evidence: Subscription auth failed overnight (2026-03-20 → 2026-03-21 ~00:14). Config reverted to API key. John sent multiple "hi" messages (00:17, 00:26, 00:29) with no response. Auth issues can cause complete failure to respond, not just error messages.
- confidence: medium — one incident, but pattern is clear
- note: Unlike API credit depletion (which errors), auth failure can be completely silent from user perspective
