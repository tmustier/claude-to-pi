# claude-to-pi

Move from Claude Code to [Pi](https://pi.dev/) — a more extensible AI coding agent. Designed for non-technical users who want an AI assistant that can search the web, manage email, create documents, and build its own new tools on the fly.

This repo gives you a one-paste bootstrap that installs Pi, copies your Claude credentials, sets up packages and extensions, and walks you through everything step by step.

## Getting started

Open Claude Code and paste this:

```
Please read ~/claude-to-pi/CLAUDE.md and follow the setup instructions. If ~/claude-to-pi doesn't exist, clone it first: gh repo clone tmustier/claude-to-pi ~/claude-to-pi — but before that, make sure gh is installed and authenticated (brew install gh && gh auth login if needed). I'm not very technical so please explain everything simply and go step by step.
```

Claude Code will:
1. Install any missing tools (Node.js, GitHub CLI, Pi)
2. Copy your Claude login to Pi (no need to sign in again)
3. Install settings, extensions, and packages
4. Tell you to open Pi and type `/onboard`

The `/onboard` command in Pi finishes the interactive setup — granting Full Disk Access, connecting services, and giving you a tour.

## What can Pi do?

Everything Claude Code can, plus:

- **"Create an HTML page showing [data]"** — builds interactive charts and dashboards, then `/open` to view in your browser
- **"Make me a slide deck about [topic]"** — generates PowerPoint files
- **"Search the web for [topic]"** — finds articles and summarises them
- **"Draft an email to [person] about [topic]"** — writes it, previews, waits for your OK before sending
- **"Read this PDF and summarise it"** — reads, merges, splits, OCRs documents
- **"Make that less AI-sounding"** — rewrites to remove generic AI patterns
- **"Can you build me a tool that does X?"** — Pi can create its own new extensions and commands

Pi is not a fixed app with buttons. It's more like a colleague who can learn new tricks. If you can describe what you want, it can probably do it — or build itself the ability to.

## Key shortcuts

| Shortcut | What it does |
|----------|-------------|
| **⌘P** | Switch AI models — Opus (empathy & taste) ↔ GPT-5.4 (raw smarts) ↔ Sonnet (speed) |
| **⇧Tab** | Toggle deep thinking on/off |
| **/** | Command palette — saved workflows |
| **Esc** | Cancel anything |

## What's included

| Category | Contents |
|----------|---------|
| **Settings** | 3 models (Opus 4.6, Sonnet 4.6, GPT-5.4), xhigh thinking, curated packages |
| **AGENTS.md** | Non-technical user guidance, outbound email safety, proactive git handling |
| **Extensions** | Startup tips (32), `/open` command, `.claude/rules/` compatibility |
| **Prompts** | `/onboard`, `/auto-pr`, `/machine-doctor`, `/bootstrap-from-claude-code` |
| **Subagents** | PR reviewer, code reviewer |
| **Scripts** | `send-gate` (60s abort window before sending emails) |
| **Skills** | `unslop` (remove AI patterns), `chrome-cookies` (extract browser sessions) |

### Packages (auto-installed)

Pi extensions, agent-browser, firecrawl (web scraping), pi-web-access, surf-cli (Chrome control), pi-design-deck, visual-explainer, pi-interview-tool, pi-side-chat, pi-autoresearch, pi-symphony, pi-agent-teams, upstream GTM skills from `refoundai/lenny-skills`, and more. Plus [impeccable](https://impeccable.style) (20+ design skills, installed separately).

## Customising for your team

This repo is designed to be forked and customised. Add your own:

- **Skills** in `skills/` — team-specific tools (CRM integrations, internal APIs, etc.)
- **Prompt templates** in `prompts/` — reusable workflows
- **Subagents** in `agents/` — specialised reviewers or workers
- **Extensions** in `extensions/` — custom commands and UI

Edit `AGENTS.template.md` to add your team's conventions, tool access, and MCP servers. Edit `settings.template.json` to add or remove packages.

## License

MIT
