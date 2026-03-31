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

## [belief] Cron jobs now use Haiku by default
- first_observed: 2026-03-22
- evidence: John requested downgrade of all scheduled jobs (Auth Monitor, Morning Brief, Daily Workspace Backup, Nightly Extraction) from Sonnet to Haiku to reduce overnight automation costs. Haiku sufficient for file/status ops.
- confidence: high
- rule: When creating cron jobs after 2026-03-22, default to `--model anthropic/claude-haiku-4-5` instead of Sonnet
- note: Supercedes earlier belief about Sonnet default

## [belief] Auth fallback protection reduces financial risk
- first_observed: 2026-03-22
- evidence: Implemented automatic recovery in 5am Auth Monitor: if subscription auth fails, downgrade Doyle to Sonnet and restart gateway. This prevents accidental API bill spikes if token auth breaks overnight.
- confidence: high
- rule: Always include fallback protections in auth-critical cron jobs
- note: John's deliberate security posture (non-admin account, manual interventions acceptable) means system must be resilient to failures

## [belief] Rate limit tolerance: slow & steady beats parallel API calls
- first_observed: 2026-03-30
- evidence: John explicitly stated preference for slower work spread over multiple days rather than parallel jobs. Rate limit hits cause stalls until manual reminder. Expressed concern about wasted time hitting ceilings.
- confidence: high
- rule: When queueing multiple analysis/research tasks, batch them into sequential cron jobs or heartbeat checks rather than spawning parallel agents. Better to space work over time and hit targets reliably than risk API exhaustion.
- note: Applies especially to quantitative analysis pipeline (rerun monte_carlo.py + healthcare bridge analysis). Schedule these as sequential Tuesday tasks, not parallel runs.
