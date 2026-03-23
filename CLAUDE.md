# Pi Bootstrap

You are helping a **non-technical user** move from Claude Code to Pi (a more extensible coding agent). They may not be comfortable with terminals — explain everything in plain language, go step by step, and confirm each step worked before moving on.

**When they type their password in the terminal, nothing will appear on screen** — no dots, no asterisks. This is normal. Warn them before any password prompt.

Work through these steps in order.

## Step 1: Prerequisites

Check what's installed:

```bash
command -v node && echo "✓ node $(node --version)" || echo "✗ node missing"
command -v npm && echo "✓ npm" || echo "✗ npm missing"
command -v git && echo "✓ git" || echo "✗ git missing"
command -v gh && echo "✓ gh" || echo "✗ gh missing"
command -v pi && echo "✓ pi" || echo "✗ pi missing"
```

For anything missing:
- **node/npm**: "You need Node.js. Go to https://nodejs.org and download the LTS version. Run the installer, then come back."
- **git**: `brew install git` (if they don't have brew: "Go to https://brew.sh, copy the install command, paste it in your terminal, and run it. It'll ask for your password — remember, nothing shows as you type.")
- **gh**: `brew install gh`
- **pi**: `npm i -g @mariozechner/pi-coding-agent`

Wait for them to install each missing tool before continuing.

## Step 2: GitHub authentication

Check: `gh auth status`

If not logged in, walk them through `gh auth login`:
1. Choose **GitHub.com**
2. Choose **HTTPS**
3. Choose **Login with a web browser**
4. It will show a one-time code — tell them to copy it
5. A browser window opens — paste the code and authorize

After login, verify: `gh auth status`

## Step 3: Clone this repo

If the claude-to-pi repo isn't already cloned:
```bash
gh repo clone tmustier/claude-to-pi ~/claude-to-pi
```

## Step 4: Install Pi and copy your credentials

Install Pi if not already:
```bash
npm i -g @mariozechner/pi-coding-agent
```

Now copy your Claude credentials into Pi so they don't have to log in again. You (Claude Code) store your Anthropic OAuth tokens in the macOS Keychain. Extract them and write to Pi's auth file:

```bash
mkdir -p ~/.pi/agent

security find-generic-password -s "Claude Code-credentials" -w 2>/dev/null | python3 -c "
import sys, json, pathlib

cc = json.loads(sys.stdin.read())
oauth = cc.get('claudeAiOauth', {})

if not oauth.get('accessToken'):
    print('No credentials found — user will need to run pi /login')
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

If that worked, explain: "I've copied your Claude login to Pi, so you won't need to sign in again."

If it didn't find credentials, tell them: "When you open Pi for the first time, run `/login` to connect your Claude account."

## Step 5: Copy settings and config

```bash
# Settings (models, packages, thinking level)
cp ~/claude-to-pi/settings.template.json ~/.pi/agent/settings.json

# AGENTS.md (agent guidelines)
cp ~/claude-to-pi/AGENTS.template.md ~/.pi/agent/AGENTS.md
```

Now **personalize AGENTS.md** — ask the user for:
- Their full name
- Their GitHub username
- Their role and company
- Their email

Edit `~/.pi/agent/AGENTS.md` and replace the placeholders in the "About You" section.

## Step 6: Install skills, agents, prompts, extensions, tools

```bash
# Repo-owned custom skills
for s in ~/claude-to-pi/skills/*/; do pi install "$s" 2>/dev/null; done

# Clean up any old local copies of skills that now come from an upstream package
for s in enterprise-sales founder-sales positioning-messaging; do
  p="$HOME/.pi/agent/skills/$s"
  [ -L "$p" ] && [ ! -e "$p" ] && rm "$p"
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

# send-gate (outbound email safety net)
mkdir -p ~/.local/bin
cp ~/claude-to-pi/scripts/send-gate ~/.local/bin/send-gate
chmod +x ~/.local/bin/send-gate
```

Make sure `~/.local/bin` is on PATH:
```bash
grep -Fq 'export PATH="$HOME/.local/bin:$PATH"' ~/.zshrc 2>/dev/null || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
```

## Step 7: Install external tools

```bash
# Firecrawl (web scraping)
command -v firecrawl >/dev/null 2>&1 || npm i -g firecrawl-cli

# Video tools (optional, for pi-web-access)
command -v ffmpeg >/dev/null 2>&1 || brew install ffmpeg
command -v yt-dlp >/dev/null 2>&1 || brew install yt-dlp
```

## Step 8: Pull Pi packages

This downloads all the packages configured in settings.json, including upstream GTM skills (`enterprise-sales`, `founder-sales`, `positioning-messaging`) from `refoundai/lenny-skills`:
```bash
pi update
```

This may take a minute. Let the user know.

## Step 9: Set up the alias

```bash
grep -q 'alias claude="pi"' ~/.zshrc 2>/dev/null || (echo '' >> ~/.zshrc && echo '# Use Pi instead of Claude Code' >> ~/.zshrc && echo 'alias claude="pi"' >> ~/.zshrc)
```

## Step 10: Hand off to Pi

Everything mechanical is done. Tell the user:

---

**You're all set up! 🎉**

From now on, type **`pi`** to start your AI assistant (or `claude` — it'll open Pi automatically).

When Pi starts, type **`/onboard`** to finish connecting your accounts. This takes about 10 minutes and mostly involves signing into things in your browser:
- Granting Full Disk Access (a macOS permission — Pi walks you through it)
- Setting up Chrome browser control
- Setting up a daily auto-update

Pi will skip anything that's already done and only ask you about the remaining bits.

**Quick shortcuts to remember:**
- **⌘P** — switch AI models (Opus for empathy/taste, GPT-5.4 for raw smarts, Sonnet for speed)
- **⇧Tab** — toggle extended thinking
- **/** — command palette
- **Esc** — cancel anything

---
