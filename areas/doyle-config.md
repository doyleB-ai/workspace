---
subject: doyle-configuration
type: area
status: active
started: 2026-03-12
owner: both
related: [facts/infrastructure, facts/accounts]
---

# Doyle Configuration

Ongoing setup and improvement of Doyle's capabilities, tools, and infrastructure.

## TODO
- [x] Turn off telemetry in Claude Code
- [x] Switch OpenClaw auth to Claude Code auth (subscription-based, no credit balance to deplete)
- [x] Overnight session reset (daily at 4 AM PT if idle 60+ min)
- [x] ~~Enable auto cache when hitting Claude API~~ (N/A — caching disabled on subscription auth)
- [x] Set auto compaction to ~50% of total context (reserveTokensFloor: 100000)
- [x] Set up different models for different contexts — Opus for chat, Haiku for compaction, Sonnet for cron jobs
- [x] Set up facts & beliefs section in memory (PARA-style) — this migration
- [ ] Update LinkedIn profile (manual steps OK)
- [ ] Draft resume
- [ ] Configure VSCode on the Mac mini — install extensions (GitLens, Error Lens, Path Intellisense, Markdown All in One, ShellCheck, YAML, DotENV, One Dark Pro, Material Icon Theme, REST Client). No Copilot.
- [ ] Review and tighten SOUL.md with explicit "NOT" behaviors
- [x] ~~Explore memory projects on GitHub~~ (PARA system is sufficient for now)
- [ ] Set up SSH access to admin account (cleary) on Mac mini

## Ideas / Backlog
- Mobile IDE access — VSCode Tunnel for browser-based IDE on mobile, or Textastic (iOS, ~$10) for native SFTP file editing

## Incident Log
- **2026-03-18:** API credit depletion caused cascading failure. Required full reboot + `openclaw doctor`. Root cause: gateway caches auth failure state. Fix: switch to Claude Code auth.
