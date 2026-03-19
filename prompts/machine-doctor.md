---
description: Audit this Mac's Pi setup, auth state, permissions, and common app installs
---
Audit and, where appropriate, repair this Mac's `pi-setup` environment.

Context:
- Live Pi dir: `~/.pi/agent`
- Do **not** assume a fixed checkout path like `~/projects/pi-setup`; infer the active repo/checkout from the current symlink targets and nearby files when needed
- The active bootstrap command is the `bootstrap.sh` from whichever checkout currently owns the linked Pi resources

Goals:
1. Verify Pi resources are set up sensibly from `~/.pi/agent`:
   - `agents/*.md`
   - `prompts/*.md`
   - `extensions/*.{ts,js}`
   - `skills/*`
   - `config/*.json`
   - `settings.json` and `AGENTS.md` may either point at this repo **or** be intentionally preserved external files/symlinks; treat both as valid unless they are clearly broken or stale
2. Verify key CLIs are installed and on PATH:
   - `brew`, `git`, `gh`, `jq`, `node`, `npm`, `python3`, `uv`, `pi`, `gog`
   - `firecrawl`, `docker`
3. Verify Pi package setup:
   - Read `~/.pi/agent/settings.json`
   - If packages/resources look missing or stale, suggest and/or run `pi update`
4. Verify common app installs (check `/Applications` and `~/Applications`):
   - Google Chrome, Microsoft Excel, Microsoft PowerPoint, Microsoft Word
   - Granola, Ghostty, Notion, Superhuman, Docker, Obsidian, Cursor
5. Check auth/login state where safe:
   - `gh auth status`
   - If `gog` auth is unclear, recommend `gog auth login`
   - If Firecrawl auth is unclear, recommend `firecrawl login --browser`
   - If LinkedIn MCP profile setup is missing, recommend `uvx linkedin-scraper-mcp --login`
6. Check likely macOS permission blockers:
   - Try reading `~/Library/Messages/chat.db`
   - If relevant paths exist, check WhatsApp Desktop data readability too
   - If access fails, explain that Full Disk Access is likely missing for the current terminal app / Pi
   - If browser or screenshot workflows are likely blocked, explain that Accessibility and Screen Recording permissions may still need approval
7. If something is easy and safe to fix with commands, fix it.
8. If a step requires GUI interaction, explain it clearly and one thing at a time.
9. Offer to open missing apps or relevant settings panes, but ask before doing anything invasive.

Working style:
- Be pragmatic and concise.
- Prefer checks and repairs that are low-risk and reversible.
- Do not overwrite user config blindly.
- If `settings.json` or `AGENTS.md` live outside this repo and appear intentional, do **not** relink them unless the user explicitly asks.
- Do not assume authentication failures are fatal; instead, identify the next manual step.

Output format:
- **Status summary**
- **Fixed automatically**
- **Needs user action**
- **Suggested next commands**
