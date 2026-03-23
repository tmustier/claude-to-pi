---
description: Finish Pi setup — Full Disk Access, Chrome control, daily updates, Claude Code migration
---

You're helping a user finish setting up their Pi environment. They may not be technical — explain everything in plain language, go one step at a time, and confirm each step worked before moving on.

**The user likely got here from the bootstrap flow** (CLAUDE.md run via Claude Code). That means Pi, settings, AGENTS.md, skills, extensions, prompts, and external tools are probably already installed. **Check what's already done before each step and skip it if complete.** Don't redo work — just confirm with a quick "✓ already done" and move on.

If nothing has been set up yet (they came here directly), work through all steps. Otherwise focus on the interactive steps that the bootstrap couldn't do.

Work through the following steps in order. **After each step, check it worked** and give a brief ✓ summary before moving on.

## Step 1: Full Disk Access

Pi needs Full Disk Access on macOS to read things like browser data and local app caches. Without it, some skills won't work.

Walk the user through granting it:

1. Open System Settings (you can run `open "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"` to jump straight there)
2. Go to **Privacy & Security → Full Disk Access**
3. Click the **+** button
4. Find and add their **terminal app** — this is whatever app they use to run Pi (e.g., Terminal, iTerm2, Ghostty, Warp). If they're not sure which one, ask them what app they typed `pi` into.
5. They may need to toggle it off and on, or restart the terminal app, for it to take effect.

Verify it worked:
```bash
ls ~/Library/Messages/chat.db 2>/dev/null && echo "✓ Full Disk Access is working" || echo "✗ Full Disk Access not granted yet"
```

If it fails, explain they need to quit and reopen their terminal app after granting access.

## Step 2: Check prerequisites

Check that `node`, `npm`, `git`, `gh`, `pi` are installed. For anything missing, give the exact install command and wait.

Also check `gh auth status`.

**Important password note:** Several steps during setup will ask for their Mac login password in the terminal. **When they type their password, nothing will appear on screen** — no dots, no asterisks, nothing. This is normal and expected! Warn them before any password prompt.

## Step 3: Pi settings

Check if `~/.pi/agent/settings.json` exists. If not, copy from `~/claude-to-pi/settings.template.json`.

Explain the models: "Opus has more empathy and taste — it's better for writing, creative work, and anything where tone matters. GPT-5.4 is smarter and more precise but very literal and less pleasant to interact with. Sonnet is a lighter, faster version of Opus for quick questions. Switch anytime with ⌘P."

## Step 4: AGENTS.md

Check if `~/.pi/agent/AGENTS.md` exists. If not, copy from `~/claude-to-pi/AGENTS.template.md` and personalize — ask for their name, GitHub username, role, company, and email.

## Step 5: Install skills, prompts, extensions

If not already done, install the repo-owned skills, prompts, and extensions from `~/claude-to-pi/`. Check if skills are already present before re-installing.

Then clean up any stale local symlinks for skills that now come from an upstream package:

```bash
for s in enterprise-sales founder-sales positioning-messaging; do
  p="$HOME/.pi/agent/skills/$s"
  [ -L "$p" ] && [ ! -e "$p" ] && rm "$p"
done
```

## Step 6: Pull packages

Run `pi update` if packages haven't been pulled yet. This also installs the upstream GTM skills `enterprise-sales`, `founder-sales`, and `positioning-messaging` from `refoundai/lenny-skills`.

## Step 7: pi-web-access setup

pi-web-access can work zero-config if the user is signed into Google in Chrome. Check if Chrome is installed:

```bash
ls "/Applications/Google Chrome.app" >/dev/null 2>&1 && echo "Chrome found" || echo "Chrome not found"
```

If Chrome is installed and they're signed into Google, it should just work. Otherwise, they can add API keys later to `~/.pi/web-search.json`.

Explain: "Pi can search the web, fetch pages, understand YouTube videos, and analyze screen recordings. If you're signed into Google in Chrome, it works automatically."

## Step 8: Impeccable (design skills)

Impeccable adds 20+ design skills (animate, polish, critique, typeset, adapt, etc.). It's not a Pi package — it installs separately.

```bash
ls ~/.agents/skills/adapt >/dev/null 2>&1 && echo "✓ Impeccable already installed" || echo "✗ Not installed"
```

If not installed, tell the user to visit [impeccable.style](https://impeccable.style), download the ZIP for Pi, and extract it. Or skip for now — design skills are nice-to-have.

## Step 9: surf-cli setup

surf-cli gives Pi direct control over your actual Chrome browser — the one you're already logged into, with all your sessions and cookies. Much better than Playwright (which spins up a separate empty browser). Walk them through it:

1. Install: `npm i -g surf-cli`
2. Get the extension path: `surf extension-path` — copy the path it prints
3. In Chrome, go to `chrome://extensions`
4. Toggle **Developer mode** on (top-right switch)
5. Click **Load unpacked**, paste the path from step 2
6. Copy the **extension ID** — the long string of letters under the Surf extension
7. Install native host: `surf install <paste-extension-id-here>`
8. **Restart Chrome completely** (quit and reopen), then test: `surf tab.list`

If it shows their open tabs, it's working.

Explain: "This lets Pi see and control your Chrome tabs directly — it can read pages you're looking at, fill forms, click buttons, all in your actual browser where you're already logged into everything."

## Step 10: Auto-update cron job

Set up a daily job at 4:04 AM to keep Pi packages updated:

```bash
(crontab -l 2>/dev/null; echo "4 4 * * * npm install -g @mariozechner/pi-coding-agent >> /tmp/pi-update.log 2>&1 && $(which pi) update >> /tmp/pi-update.log 2>&1") | crontab -
```

Explain: "I've set up a daily job that keeps your Pi packages updated automatically. You don't need to think about it."

## Step 11: Migrate from Claude Code

Check if Claude Code is installed: `command -v claude >/dev/null 2>&1`

If found:

1. Check for custom commands/skills in `~/.claude/commands/` and `~/.claude/skills/`
2. **Pi does not auto-discover Claude Code skills.** Ask the user if they want to keep any of them.
3. Simple slash commands → convert to Pi prompt templates now
4. Skills that already exist in Pi → tell the user and skip
5. Complex items → create a todo in `~/todo/` with the original content and a migration plan

Set up the alias if not already done:
```bash
grep -q 'alias claude="pi"' ~/.zshrc 2>/dev/null || {
  echo '' >> ~/.zshrc
  echo 'alias claude="pi"' >> ~/.zshrc
}
```

Note: Pi already reads `CLAUDE.md` files and the `claude-rules` extension picks up `.claude/rules/` folders. Project-level Claude Code configuration carries over automatically.

## Step 12: Quick orientation

Give them a brief tour:

- **⌘P** switches between models — Opus for empathy and taste, GPT-5.4 for raw smarts, Sonnet for speed
- **⇧Tab** toggles extended thinking — on by default, turn off for simple questions
- **/** opens the command palette — `/auto-pr`, `/machine-doctor`, etc.
- **`/open`** opens any file from Pi in their default app
- They can just ask in natural language — write documents, search the web, create HTML dashboards, draft emails
- **If Pi can't do something yet**, just ask: "Can you build me a tool that does X?" — it can extend itself

Ask if they have any questions or want to try anything out!
