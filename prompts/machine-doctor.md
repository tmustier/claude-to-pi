---
description: Audit this Mac's Pi setup, auth state, permissions, packages, and common blockers
---

Audit and, where safe, repair this Mac's Pi environment.

Context:

- Live Pi dir: `~/.pi/agent`
- Do **not** assume a fixed checkout path; infer the active `claude-to-pi` checkout from symlink targets, copied files, or `~/claude-to-pi` when present.
- Do not overwrite intentional user config blindly.

Start with the deterministic health runner from the active checkout:

```bash
/path/to/claude-to-pi/scripts/setup-health --live --json
```

Resolve the path rather than assuming `/path/to`. The trusted manifest checks command availability, versions, package sources, broken symlinks, self-contained helper runtimes, and safe live probes without printing command output. Use its structured failures as the first repair queue, then perform the qualitative checks below. Do not automatically upgrade packages merely because a check fails.

Goals:

1. Verify Pi resources are set up sensibly in `~/.pi/agent`:
   - `settings.json`
   - `AGENTS.md`
   - `agents/*.md`
   - `prompts/*.md`
   - `extensions/*.{ts,js}`
   - `scripts/send-gate` or `~/.local/bin/send-gate`
   - `scripts/papercut` or `~/.local/bin/papercut`
2. Verify key CLIs are installed and on PATH:
   - `brew`, `git`, `gh`, `jq`, `node`, `npm`, `python3`, `pi`
   - Optional but useful: `ffmpeg`, `yt-dlp`, `surf`
   - If `send-gate` or `papercut` is missing or older than the active checkout copy, install it into `~/.local/bin/` and make it executable
   - Verify `papercut resolve --json` and a sanitized `papercut --dry-run` succeed; do not append or submit a real note during the audit
3. Verify Pi package setup:
   - Read `~/.pi/agent/settings.json`
   - Check that the default package list is small and current: `pi-subagents`, `pi-mcp-adapter`, `tmustier/pi-auto-compact@v0.1.2`, `pi-web-access`, `surf-cli`, document skills, and `tmustier/claude-to-pi` skills
   - Confirm `~/.pi/agent/auto-compact.json` is valid and uses 200,000 tokens when the user has no intentional override
   - Flag an active `model-compaction-trigger.ts`, `soft-context-compaction.json`, or another proactive-compaction package as a potential duplicate trigger; preserve a timestamped backup when disabling it
   - If packages/resources look missing or stale, suggest and/or run `pi update --extensions`
   - Confirm `AGENTS.md` contains the Pi-aware papercut metadata/safety policy and `prompts/papercuts-review.md` exists; preserve intentional customizations when repairing them
   - Confirm `extensions/papercut.ts` is loaded and exposes the `papercut` tool plus `/papercuts-submit`; do not invoke the tool merely as a setup test
4. Verify model setup:
   - Check `enabledModels` / scoped model defaults
   - Flag stale model names such as `gpt-5.5`, `gpt-5.4`, `gpt-5`, `o3`, `o1`, Claude 3.x, or older Claude 4.x aliases
   - If auth is missing for a configured provider, recommend `/login` rather than silently changing models
5. Verify common app installs where relevant:
   - Google Chrome, terminal app, Microsoft Office apps if document workflows matter
   - Optional apps the user cares about: Granola, Ghostty, Notion, Superhuman, Docker, Obsidian, Cursor
   - cmux is optional, but **if** it is installed (`cmux` on PATH or `/Applications/cmux.app`) and `~/.pi/agent/extensions/cmux-session.ts` is missing, run `cmux hooks pi install --yes` (bundled CLI: `/Applications/cmux.app/Contents/Resources/bin/cmux`). Without these hooks cmux guesses Pi session↔pane bindings from the newest session file per cwd and can duplicate or swap same-cwd Pi tabs when restoring after a crash
   - If the active checkout has `shell/zshrc.claude-to-pi` but `~/.zshrc` does not source it, offer to append `[ -r ~/claude-to-pi/shell/zshrc.claude-to-pi ] && source ~/claude-to-pi/shell/zshrc.claude-to-pi` (adjust the path if the checkout lives elsewhere, and `brew install zsh-autosuggestions` if missing) — inline shell autosuggestions plus the `yolo` Pi alias
6. Check auth/login state where safe:
   - `gh auth status`
   - If Claude Code credentials exist, confirm whether Pi has copied Anthropic auth
   - If OpenAI/Codex auth is missing, explain that `/login` can add it
7. Check likely macOS permission blockers:
   - Try reading `~/Library/Messages/chat.db`
   - If access fails, explain that Full Disk Access is likely missing for the current terminal app / Pi
   - If browser automation or screenshots are likely blocked, explain Accessibility and Screen Recording permissions may still need approval
8. Browser automation:
   - Flag a leftover `agent-browser` package as retired; `surf-cli` is the supported browser automation path
   - Check whether `surf` is installed and whether `surf tab.list` works
   - If `surf` is not configured, give the native-host setup steps, but do not force it
9. If something is easy and safe to fix with commands, fix it.
10. If a step requires GUI interaction, explain it clearly and one thing at a time.

Working style:

- Be pragmatic and concise.
- Prefer checks and repairs that are low-risk and reversible.
- Do not relink or overwrite `settings.json` / `AGENTS.md` if they appear intentionally customized.
- Do not assume authentication failures are fatal; identify the next manual step.

Output format:

- **Status summary**
- **Fixed automatically**
- **Needs user action**
- **Suggested next commands**
