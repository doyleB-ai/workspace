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
