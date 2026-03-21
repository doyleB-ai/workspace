# MEMORY.md — Boot Pointer

This file exists so OpenClaw auto-loads it at session start.
All memory now lives in the PARA structure below. Read INDEX.md for the full map.

## How to load memory

At session start, read these files:
1. `INDEX.md` — full map of everything Doyle knows
2. `facts/john.md` — who John is (always relevant)
3. `beliefs/communication.md` — how John prefers to communicate (always relevant)

For specific topics, use memory_search or read the relevant file directly:
- facts/ — verified facts about John, infrastructure, accounts
- beliefs/ — Doyle's formed beliefs with evidence trails
- projects/ — active work (recruiting, etc.)
- areas/ — ongoing responsibilities (Doyle config, NDS team)
- resources/ — reference material
- archive/ — historical session logs and legacy files
