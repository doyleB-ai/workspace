---
subject: openclaw-reference
type: resource
last_updated: 2026-03-19
related: [facts/infrastructure, areas/doyle-config]
---

# OpenClaw Reference

## CLI
- Binary not in PATH — use: `/Users/clearyclaw/claws/node_modules/.bin/openclaw`
- Config: `~/.openclaw/openclaw.json`
- Recovery: `openclaw doctor` can fix gateway/session issues

## Key Paths
- Workspace: `~/.openclaw/workspace/`
- Memory DB: `~/.openclaw/memory/main.sqlite`
- Agent sessions: `~/.openclaw/agents/main/sessions/`

## Session Management
- Sessions can be reset via overnight cron (planned)
- Gateway caches auth failure state — may require reboot to recover after API issues

## Learning Resources for John
- [ ] Explain sessions — what they are, how they work, how to optimize them
- [ ] macOS education: plists, LaunchDaemons/Agents, file system structure
- [ ] Find good YouTube resources on macOS internals / terminal basics
