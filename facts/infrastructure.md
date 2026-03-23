---
subject: infrastructure
type: fact
last_verified: 2026-03-19
related: [facts/accounts]
---

# Infrastructure

## Mac Mini
- Machine: John's Mac mini (Johns-Mac-mini), Austin TX
- OS: macOS (Darwin 25.2.0, arm64)
- User account: clearyclaw (standard user, non-admin)
- Admin account: cleary (separate)
- Auto-login: enabled for clearyclaw account on restart

## OpenClaw
- Version: 2026.3.12
- Running as: LaunchDaemon (system-level, 24/7, survives logouts and reboots)
- LaunchDaemon plist: /Library/LaunchDaemons/ai.openclaw.gateway.plist

## Network Access
- Tailscale IP: 100.120.74.29 (Mac mini)
- SSH: accessible via `ssh clearyclaw@100.120.74.29` or `ssh doyle` (from laptop)
- VSCode Remote SSH configured on John's laptop (Aprils MacBook Air)

## Doyle Model & Auth Configuration
- **Primary model:** `anthropic/claude-opus-4-6` (as of 2026-03-22)
- **Auth priority:** `anthropic:manual` (subscription token) → `anthropic:default` (API key fallback)
- **Subscription status:** Active; confirmed via gateway logs and test ($16.23 balance unchanged after ~$2 token burn)
- **API key fallback protection:** 5am Auth Monitor checks for fallback; if detected, auto-downgrade to Sonnet and restart gateway

## Scheduled Automation (Cron Jobs)
- **5am:** Auth Monitor (Haiku, checks subscription auth status, auto-recovery enabled)
- **6:30am:** Morning Brief (Haiku)
- **11pm:** Daily Workspace Backup (Haiku)
- **11pm:** Nightly Extraction (Haiku)
- **Note:** All scheduled jobs use Haiku (cost optimized) instead of Sonnet as of 2026-03-22
