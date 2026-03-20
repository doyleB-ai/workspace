# TROUBLESHOOTING.md — Doyle's Break-Glass Guide

If Doyle is unresponsive, erroring, or acting weird — start here.

---

## 🔴 Doyle isn't responding / keeps erroring

### Step 1: Check gateway status
```
openclaw gateway status
```
If it says stopped or failed → restart it:
```
openclaw gateway restart
```

### Step 2: Run the doctor
```
openclaw doctor
```
This checks config, connectivity, and auth. Follow any suggestions it gives.

### Step 3: Full reboot (nuclear option)
If the above doesn't work, restart the Mac mini. OpenClaw runs as a LaunchDaemon and will come back up automatically on reboot.

---

## 🟡 Error: "API credits exhausted" or billing errors

This means the Anthropic API credit balance hit zero.

1. Go to https://console.anthropic.com → Billing → Add credits
2. After adding credits, **don't just wait** — the session may be stuck in a bad state
3. Run: `openclaw gateway restart`
4. If still broken: reboot the Mac mini

**Long-term fix:** Switch to Claude Code auth (uses your Anthropic subscription — no separate credit balance). This is on the to-do list.

---

## 🟡 Doyle seems confused / doesn't remember things

Memory lives in files. If something seems off:
- Check `/Users/clearyclaw/.openclaw/workspace/MEMORY.md`
- Check `/Users/clearyclaw/.openclaw/workspace/memory/` for daily notes

You can tell Doyle: "Read your memory files" and he'll reload context.

---

## 🟡 Messages are being sent but no reply

1. Check Telegram bot is alive — try sending `/start` to @DoyleB_bot
2. Check gateway: `openclaw gateway status`
3. Check logs: `openclaw gateway logs` (or `openclaw logs`)

---

## 🔵 General commands to know

| What | Command |
|------|---------|
| Check status | `openclaw status` |
| Gateway status | `openclaw gateway status` |
| Restart gateway | `openclaw gateway restart` |
| Run diagnostics | `openclaw doctor` |
| View logs | `openclaw gateway logs` |

---

## SSH in from laptop (if needed)
```
ssh doyle
```
or
```
ssh clearyclaw@100.120.74.29
```

---

*If none of this works: reboot the Mac mini. It runs as a system daemon and will restart automatically.*
