# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Google Docs

- **Doyle Troubleshooting Guide**
  - Doc ID: `1Ax2uRVNzmCSGtx_Mtn0j2RL1kGiMW8aS6Tpt3rdk_ic`
  - URL: https://docs.google.com/document/d/1Ax2uRVNzmCSGtx_Mtn0j2RL1kGiMW8aS6Tpt3rdk_ic/edit
  - ⚠️ **Rule:** Whenever `TROUBLESHOOTING.md` is updated, immediately sync to this doc:
    ```
    gog docs clear 1Ax2uRVNzmCSGtx_Mtn0j2RL1kGiMW8aS6Tpt3rdk_ic --account clearyclaw@gmail.com
    gog docs write 1Ax2uRVNzmCSGtx_Mtn0j2RL1kGiMW8aS6Tpt3rdk_ic --file /Users/clearyclaw/.openclaw/workspace/TROUBLESHOOTING.md --account clearyclaw@gmail.com
    ```

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
