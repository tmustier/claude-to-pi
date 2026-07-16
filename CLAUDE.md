# Pi Bootstrap

You are helping a **non-technical user** move from Claude Code to Pi. They may not be comfortable with terminals — explain everything in plain language, go step by step, and confirm each step worked before moving on.

**When they type their password in the terminal, nothing will appear on screen** — no dots, no asterisks. This is normal. Warn them before any password prompt.

Work through these steps in order.

## Step 1: Prerequisites

First, check if Homebrew is installed:

```bash
if command -v brew >/dev/null 2>&1; then
  echo "✓ Homebrew installed"
else
  echo "✗ Homebrew missing — installing..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [[ -f /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
    grep -Fq '/opt/homebrew/bin/brew' ~/.zprofile 2>/dev/null || {
      echo >> ~/.zprofile
      echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
    }
  fi
fi
```

**Note:** Homebrew may ask for the user's Mac password — remind them that nothing appears on screen when typing it.

Then check the rest:

```bash
command -v node && echo "✓ node $(node --version)" || echo "✗ node missing"
command -v npm && echo "✓ npm $(npm --version)" || echo "✗ npm missing"
command -v git && echo "✓ git $(git --version)" || echo "✗ git missing"
command -v gh && echo "✓ gh $(gh --version | head -n 1)" || echo "✗ gh missing"
command -v pi && echo "✓ pi $(pi --version 2>/dev/null || echo '(installed)')" || echo "✗ pi missing"
command -v uv && echo "✓ $(uv --version)" || echo "✗ uv missing"
```

For anything missing:

- **node/npm**: "You need Node.js. Go to https://nodejs.org and download the LTS version. Run the installer, then come back."
- **git**: `brew install git`
- **gh**: `brew install gh`
- **uv**: `brew install uv`
- **pi**: Will be installed/updated in Step 4.

Wait for them to install each missing tool before continuing.

## Step 2: GitHub authentication

Check:

```bash
gh auth status
```

If not logged in, walk them through `gh auth login`:

1. Choose **GitHub.com**
2. Choose **HTTPS**
3. Choose **Login with a web browser**
4. Copy the one-time code
5. Authorize in the browser

After login, verify with `gh auth status`.

## Step 3: Clone this repo

If the `claude-to-pi` repo is not already cloned:

```bash
gh repo clone tmustier/claude-to-pi ~/claude-to-pi
```

## Step 4: Install or update Pi, then copy Claude credentials

Always install/update Pi to the latest version:

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
```

Now copy Claude Code's Anthropic credentials into Pi so the user usually does not need to log in again:

```bash
mkdir -p ~/.pi/agent

security find-generic-password -s "Claude Code-credentials" -w 2>/dev/null | python3 -c "
import sys, json, pathlib

raw = sys.stdin.read().strip()
if not raw:
    print('No Claude Code credentials found — user can run pi /login later')
    sys.exit(0)

cc = json.loads(raw)
oauth = cc.get('claudeAiOauth', {})

if not oauth.get('accessToken'):
    print('No Claude Code credentials found — user can run pi /login later')
    sys.exit(0)

auth = {
    'anthropic': {
        'type': 'oauth',
        'refresh': oauth['refreshToken'],
        'access': oauth['accessToken'],
        'expires': oauth['expiresAt']
    }
}

auth_path = pathlib.Path.home() / '.pi' / 'agent' / 'auth.json'
if auth_path.exists():
    existing = json.loads(auth_path.read_text())
    existing['anthropic'] = auth['anthropic']
    auth = existing

auth_path.write_text(json.dumps(auth, indent=2))
print('✓ Copied Anthropic credentials to Pi')
"
```

If that worked, explain: "I've copied your Claude login to Pi, so you shouldn't need to sign in again."

If no credentials were found, explain: "No problem — when you open Pi, run `/login` and connect your account."

## Step 5: Copy settings and AGENTS.md

```bash
mkdir -p ~/.pi/agent

# Settings: current scoped models, compaction defaults, and a small default package set
cp ~/claude-to-pi/settings.template.json ~/.pi/agent/settings.json

# Persisted native compaction after tool-bearing turns cross 200,000 estimated tokens
if [ ! -f ~/.pi/agent/auto-compact.json ]; then
  cp ~/claude-to-pi/auto-compact.json ~/.pi/agent/auto-compact.json
fi

# AGENTS.md: your standing instructions for Pi
cp ~/claude-to-pi/AGENTS.template.md ~/.pi/agent/AGENTS.md
```

Now **personalize AGENTS.md**. Ask the user for:

- Their full name
- Their GitHub username
- Their role and company
- Their email

Edit `~/.pi/agent/AGENTS.md` and replace the placeholders in the "About You" section.

## Step 6: Install prompts, extensions, agents, and local scripts

Skills are loaded through `settings.json` and Pi packages. **Do not run `pi install` on individual skill directories** — Agent Skill folders are not Pi packages, and installing them that way can make Pi try to load skills as extensions.

```bash
# Clean up stale entries from older setup attempts.
python3 - <<'PY'
import json, pathlib

settings_path = pathlib.Path.home() / '.pi' / 'agent' / 'settings.json'
settings = json.loads(settings_path.read_text())

settings['packages'] = [
    pkg for pkg in settings.get('packages', [])
    if not (
        isinstance(pkg, str)
        and 'claude-to-pi/skills/' in pkg
    )
]

# If the user already has Claude Code or Codex skills, let Pi discover them too.
skills = settings.setdefault('skills', [])
for candidate in ['~/.claude/skills', '~/.codex/skills']:
    expanded = pathlib.Path(candidate).expanduser()
    if expanded.exists() and candidate not in skills:
        skills.append(candidate)

settings_path.write_text(json.dumps(settings, indent=2) + '\n')
PY

# Remove old local skill symlinks that would duplicate package-managed skills.
for s in enterprise-sales founder-sales positioning-messaging agent-friendly-design chrome-cookies customer-intel tmux todo-audit unslop; do
  p="$HOME/.pi/agent/skills/$s"
  [ -L "$p" ] && rm "$p"
done

# Subagents
mkdir -p ~/.pi/agent/agents
cp ~/claude-to-pi/agents/*.md ~/.pi/agent/agents/

# Prompt templates
mkdir -p ~/.pi/agent/prompts
cp ~/claude-to-pi/prompts/*.md ~/.pi/agent/prompts/

# Extensions
mkdir -p ~/.pi/agent/extensions
cp ~/claude-to-pi/extensions/*.ts ~/.pi/agent/extensions/

# Disable the superseded local compaction extension and config while preserving backups.
STAMP="$(date +%Y%m%d%H%M%S)"
if [ -f ~/.pi/agent/extensions/model-compaction-trigger.ts ]; then
  mv ~/.pi/agent/extensions/model-compaction-trigger.ts ~/.pi/agent/extensions/model-compaction-trigger.ts.disabled-"$STAMP"
fi
if [ -f ~/.pi/agent/soft-context-compaction.json ]; then
  mv ~/.pi/agent/soft-context-compaction.json ~/.pi/agent/soft-context-compaction.json.disabled-"$STAMP"
fi

# Local helpers: outbound email safety and append-only workflow-friction notes
mkdir -p ~/.local/bin
cp ~/claude-to-pi/scripts/send-gate ~/.local/bin/send-gate
cp ~/claude-to-pi/scripts/papercut ~/.local/bin/papercut
chmod +x ~/.local/bin/send-gate ~/.local/bin/papercut ~/claude-to-pi/scripts/setup-health
ln -sfn ~/claude-to-pi/scripts/setup-health ~/.local/bin/setup-health
```

`papercut` lets agents record small, sanitized workflow friction without interrupting the task. The Pi-aware extension automatically adds the active session JSONL reference, model, thinking level, context estimate, session size/entry counts, and Pi version. It never uploads prompts, messages, tool results, or JSONL contents. Captures stay local unless the user invokes `/papercuts-submit owner/repository`; `/papercuts-review` remains explicit and local.

Make sure `~/.local/bin` is on PATH:

```bash
grep -Fq 'export PATH="$HOME/.local/bin:$PATH"' ~/.zshrc 2>/dev/null || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

## Step 7: Optional external tools

The default packages mostly install themselves via `pi update`. These extra tools improve media/web workflows:

```bash
# Video tools for YouTube/video analysis in pi-web-access
command -v ffmpeg >/dev/null 2>&1 || brew install ffmpeg
command -v yt-dlp >/dev/null 2>&1 || brew install yt-dlp
```

If the user wants browser automation via `surf-cli`, finish that later from `/onboard`; it requires a Chrome extension and native host setup.

## Step 8: Pull Pi packages

This downloads the packages configured in `settings.json`, including `tmustier/pi-auto-compact@v0.1.2`:

```bash
pi update --extensions
```

This may take a few minutes. Let the user know. Run `setup-health --quick --summary`, then `/reload` and `/auto-compact` inside Pi to confirm the installation and 200,000-token default policy.

## Step 9: Hand off to Pi

Everything mechanical is done. Tell the user:

---

**You're set up!**

From now on, type **`pi`** to start your AI assistant.

When Pi starts, type **`/onboard`** to finish the interactive setup. Pi will check what is already done and skip completed steps.

**Quick orientation:**

- **Ctrl+P** — cycle scoped models; use **`/scoped-models`** to choose which models appear.
- **Shift+Tab** — cycle thinking level.
- **Alt+Enter** — queue a follow-up message for after Pi finishes working.
- **`/tree`** or **Esc twice while idle** — open the conversation tree, branch, fork, or move through history.
- **`/name <name>`** — name important sessions so `/resume` is easier.
- **`/reload`** — hot-reload new extensions, skills, prompts, and context files.
- **`/hotkeys`** — see the full current shortcut list.

Pi has excellent local docs and can extend itself. If something feels missing, ask: **"Can you check Pi's docs and add the lightest-weight way to do X?"**

---
