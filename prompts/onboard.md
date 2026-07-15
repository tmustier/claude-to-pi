---
description: Finish Pi setup — permissions, browser automation, package pull, and orientation
---

You're helping a user finish setting up their Pi environment. They may not be technical — explain everything in plain language, go one step at a time, and confirm each step worked before moving on.

The user likely got here from the bootstrap flow (`CLAUDE.md` run via Claude Code). That means Pi, settings, AGENTS.md, prompts, extensions, and packages may already be installed. **Check before each step and skip anything already done.**

Pi intentionally starts lean. The goal is not to install every shiny package. Start with a useful small setup, notice friction, and add exactly what the user needs.

## Step 1: Full Disk Access

Pi may need Full Disk Access on macOS to read local app data such as Messages, browser data, and caches.

Walk the user through granting it:

1. Open System Settings. You can run:
   ```bash
   open "x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles"
   ```
2. Go to **Privacy & Security → Full Disk Access**.
3. Click **+**.
4. Add the terminal app they use to run Pi — Terminal, iTerm2, Ghostty, Warp, etc.
5. Quit and reopen the terminal app if access still fails.

Verify:

```bash
ls ~/Library/Messages/chat.db 2>/dev/null && echo "✓ Full Disk Access is working" || echo "✗ Full Disk Access not granted yet"
```

If it fails, explain that they probably need to restart the terminal after granting access.

## Step 2: Check prerequisites

```bash
command -v brew >/dev/null 2>&1 && echo "✓ Homebrew" || echo "✗ Homebrew missing"
command -v node >/dev/null 2>&1 && echo "✓ node $(node --version)" || echo "✗ node missing"
command -v npm >/dev/null 2>&1 && echo "✓ npm $(npm --version)" || echo "✗ npm missing"
command -v git >/dev/null 2>&1 && echo "✓ git $(git --version)" || echo "✗ git missing"
command -v gh >/dev/null 2>&1 && echo "✓ gh $(gh --version | head -n 1)" || echo "✗ gh missing"
command -v pi >/dev/null 2>&1 && echo "✓ pi $(pi --version 2>/dev/null || echo installed)" || echo "✗ pi missing"
```

For anything missing, give the exact command. Typical fixes:

```bash
brew install git gh
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
```

Also check GitHub auth:

```bash
gh auth status
```

Password note: if a command asks for their Mac password, nothing will appear while typing. That is normal.

## Step 3: Pi settings and model scope

Check whether settings exist:

```bash
test -f ~/.pi/agent/settings.json && echo "✓ settings.json exists" || echo "✗ settings.json missing"
```

If missing, copy the template:

```bash
mkdir -p ~/.pi/agent
cp ~/claude-to-pi/settings.template.json ~/.pi/agent/settings.json
```

Check `~/.pi/agent/auto-compact.json`. If it is missing, copy `~/claude-to-pi/auto-compact.json` there. Preserve an existing valid policy unless the user asks to reset it to the 200,000-token default.

Explain model scope in plain language:

- `Ctrl+P` cycles through the scoped model list.
- `/scoped-models` lets them choose which models appear and in what order.
- This setup defaults to `anthropic/claude-opus-4-8` so Claude Code users can usually start with their copied Anthropic login.
- `openai-codex/gpt-5.6-sol` is included as the precision/code-review model once OpenAI/Codex auth is connected.

If OpenAI/Codex is not connected, tell them they can run `/login` later.

## Step 4: AGENTS.md

Check whether `~/.pi/agent/AGENTS.md` exists. If not, copy and personalize it:

```bash
mkdir -p ~/.pi/agent
cp ~/claude-to-pi/AGENTS.template.md ~/.pi/agent/AGENTS.md
```

Ask for:

- Full name
- GitHub username
- Role and company
- Email

Then edit the "About You" section.

## Step 5: Skills, prompts, extensions, and scripts

Skills are loaded by Pi package/settings discovery. **Do not run `pi install` on individual skill directories.**

Run the safe setup pass:

```bash
python3 - <<'PY'
import json, pathlib

settings_path = pathlib.Path.home() / '.pi' / 'agent' / 'settings.json'
settings = json.loads(settings_path.read_text())

auto_compact = 'git:github.com/tmustier/pi-auto-compact@v0.1.1'
settings['packages'] = [
    auto_compact if isinstance(pkg, str) and 'tmustier/pi-auto-compact' in pkg else pkg
    for pkg in settings.get('packages', [])
    if not (isinstance(pkg, str) and 'claude-to-pi/skills/' in pkg)
]

if auto_compact not in settings['packages']:
    settings['packages'].append(auto_compact)

skills = settings.setdefault('skills', [])
for candidate in ['~/.claude/skills', '~/.codex/skills']:
    expanded = pathlib.Path(candidate).expanduser()
    if expanded.exists() and candidate not in skills:
        skills.append(candidate)

settings_path.write_text(json.dumps(settings, indent=2) + '\n')
PY

for s in enterprise-sales founder-sales positioning-messaging agent-friendly-design chrome-cookies customer-intel tmux todo-audit unslop; do
  p="$HOME/.pi/agent/skills/$s"
  [ -L "$p" ] && rm "$p" && echo "Removed stale symlink: $s"
done

mkdir -p ~/.pi/agent/agents ~/.pi/agent/prompts ~/.pi/agent/extensions ~/.local/bin
cp ~/claude-to-pi/agents/*.md ~/.pi/agent/agents/
cp ~/claude-to-pi/prompts/*.md ~/.pi/agent/prompts/
cp ~/claude-to-pi/extensions/*.ts ~/.pi/agent/extensions/
cp ~/claude-to-pi/scripts/send-gate ~/.local/bin/send-gate
chmod +x ~/.local/bin/send-gate

# Disable the superseded compaction implementation and preserve timestamped backups.
STAMP="$(date +%Y%m%d%H%M%S)"
if [ -f ~/.pi/agent/extensions/model-compaction-trigger.ts ]; then
  mv ~/.pi/agent/extensions/model-compaction-trigger.ts ~/.pi/agent/extensions/model-compaction-trigger.ts.disabled-"$STAMP"
fi
if [ -f ~/.pi/agent/soft-context-compaction.json ]; then
  mv ~/.pi/agent/soft-context-compaction.json ~/.pi/agent/soft-context-compaction.json.disabled-"$STAMP"
fi
```

## Step 6: Pull packages

Run:

```bash
pi update
```

Explain: this updates Pi and downloads the packages listed in `settings.json`, including `tmustier/pi-auto-compact@v0.1.1`. It may take a few minutes. Run `/reload`, then `/auto-compact`, to confirm the 200,000-token default policy.

## Step 7: Browser automation

This setup includes two browser options:

- `agent-browser` — strong general browser automation; use it when Pi needs to open pages, click, fill forms, test web apps, or take screenshots.
- `surf-cli` — controls the user's real Chrome profile via a Chrome extension/native host, useful when logged-in browser state matters.

For `surf-cli`, walk through only if the user wants live-Chrome control now:

1. Install CLI if missing:
   ```bash
   npm install -g surf-cli
   ```
2. Get extension path:
   ```bash
   surf extension-path
   ```
3. Open `chrome://extensions` in Chrome.
4. Turn **Developer mode** on.
5. Click **Load unpacked** and select the path from step 2.
6. Copy the extension ID.
7. Install native host:
   ```bash
   surf install <extension-id>
   ```
8. Restart Chrome completely.
9. Test:
   ```bash
   surf tab.list
   ```

If this is too much for now, skip it. Pi can still use `agent-browser` or normal web-fetch/search tools.

## Step 8: MCP, only when useful

`pi-mcp-adapter` is installed as a default package, but do not add MCP servers just because they exist.

Explain:

- Use a simple CLI + Agent Skill when that is enough.
- Use MCP when Pi needs a real external execution surface or maintained integration.
- If they name a service, ask Pi to check whether a current MCP package/config exists.

## Step 9: Optional isolation and secrets

Do **not** configure heavy safety infrastructure by default. Mention options only if relevant:

- Secrets brokering via Infisical / agent-vault-style workflows.
- Tool sandboxing via a local micro-VM / `pi-gondolin` style setup.

## Step 10: Migrate from Claude Code

Check if Claude Code exists:

```bash
command -v claude >/dev/null 2>&1 && echo "Claude Code command found" || echo "Claude Code command not found"
```

If found:

1. Check `~/.claude/commands/` and `~/.claude/skills/`.
2. Simple slash commands can become Pi prompt templates in `~/.pi/agent/prompts/`.
3. Existing Claude/Codex Agent Skills can be loaded from settings when those directories exist.
4. Complex migration items should become small follow-up tasks, not a rushed all-at-once conversion.

### Optional alias: `claude` → `pi`

Ask before doing this. Be explicit: it changes what happens when they type `claude`.

If they say yes:

```bash
grep -q 'alias claude="pi"' ~/.zshrc 2>/dev/null || {
  echo '' >> ~/.zshrc
  echo '# Use Pi instead of Claude Code' >> ~/.zshrc
  echo 'alias claude="pi"' >> ~/.zshrc
}
```

If they say no, leave it alone.

## Step 11: Quick orientation

Give this tour:

- **Ctrl+P** cycles scoped models; use **`/scoped-models`** to edit the list.
- **Shift+Tab** cycles thinking level. `/hotkeys` is the source of truth if their keybindings differ.
- **Alt+Enter** queues a follow-up message that waits until Pi finishes all current work.
- **Enter while Pi is working** queues steering for the active turn.
- **`/tree`** or **Esc twice while idle** opens the conversation tree for branch/fork/time-travel control.
- **`/name <name>`** names a session so `/resume` is easier.
- **`/reload`** hot-reloads extensions, skills, prompts, and context files.
- **Pi can read its own docs** and can extend itself. If something is missing, ask it to check docs and add the lightest-weight solution.

Ask whether they want to try a small real task now.
