# claude-to-pi

Move from Claude Code to [Pi](https://pi.dev/) — a small, highly-extensible terminal coding agent. Pi intentionally starts lean: a few strong built-in tools, excellent local docs, and extension points for almost everything else.

This repo gives Claude Code a one-paste migration path: install/update Pi, copy your Claude credentials, install a small set of useful defaults, and then let Pi help you extend only what you actually need.

## Getting started

Open Claude Code and paste this:

```text
Please read ~/claude-to-pi/CLAUDE.md and follow the setup instructions. If ~/claude-to-pi doesn't exist, clone it first: gh repo clone tmustier/claude-to-pi ~/claude-to-pi — but before that, make sure gh is installed and authenticated (brew install gh && gh auth login if needed). I'm not very technical so please explain everything simply and go step by step.
```

Claude Code will:

1. Install any missing prerequisites and update Pi.
2. Copy your Claude login to Pi, if Claude Code has one saved.
3. Install a lightweight Pi setup: settings, AGENTS.md, prompts, extensions, and selected packages.
4. Tell you to open Pi and type `/onboard` for the interactive bits.

The `/onboard` prompt in Pi finishes setup — Full Disk Access, browser automation, optional Claude Code migration, and a quick tour.

## Current Pi mental model

Pi is not a fixed app with a huge default feature set. It is a minimal harness that can be shaped with:

- **Agent Skills** — markdown workflows and tool instructions loaded on demand.
- **Prompt templates** — slash commands such as `/onboard` or `/machine-doctor`.
- **Extensions** — TypeScript modules that can add tools, commands, keybindings, UI, model providers, compaction, and safety gates.
- **Pi Packages** — reusable bundles of extensions, skills, prompts, and themes from npm or git.

Pi can read its own local docs. If something feels missing, ask Pi to check its docs and either configure an existing extension/package or build a small one for your workflow. Use `/reload` after changing extensions, skills, prompts, or context files in a running session.

## Native shortcuts to know

Run `/hotkeys` inside Pi for the authoritative list; shortcuts are user-customisable. Current high-use defaults:

| Shortcut / command | What it does |
| --- | --- |
| **Ctrl+P** / **Shift+Ctrl+P** | Cycle forward/back through your scoped model list. |
| **`/scoped-models`** | Choose which models Ctrl+P cycles through, and save the order. |
| **Shift+Tab** | Cycle thinking level. |
| **Alt+Enter** | Queue a follow-up message that sends only after Pi finishes all current work. |
| **Enter while Pi is working** | Queue steering for the active turn, similar to Claude Code-style interruption. |
| **`/tree`** or **Esc twice while idle** | Open the conversation tree; branch, fork, and move through history. |
| **`/name <name>`** | Name the session so `/resume` is easier later. |
| **`/reload`** | Hot-reload extensions, skills, prompts, and context files. |

## What this repo installs

This repo aims for useful defaults without turning Pi into a giant pre-bundled distro.

| Category | Contents |
| --- | --- |
| **Settings** | Current Anthropic/OpenAI-Codex scoped models, xhigh thinking, Pi compaction defaults, and a small default package set. |
| **AGENTS.md** | Plain-language working style, current model policy, git hygiene, send-gate, and non-interactive command guidance. |
| **Extensions** | `/open`, startup tips, non-interactive bash guardrails, `.claude/rules/` compatibility, `/update`, and persisted native auto-compaction. |
| **Prompts** | `/onboard`, `/machine-doctor`, `/auto-pr`, `/bootstrap-from-claude-code`. |
| **Subagents** | PR reviewer and general reviewer agent definitions. |
| **Scripts** | `send-gate` — a 60s abort window before outbound email sends. |
| **Skills** | `agent-friendly-design`, `chrome-cookies`, `customer-intel`, `tmux`, `todo-audit`, `unslop`. |

### Default packages

The template keeps package defaults deliberately small:

- `pi-subagents` — chains, parallel/background agents, and dynamic workflows.
- `pi-mcp-adapter` — MCP support when you decide you need it.
- `pi-auto-compact` — persisted native compaction after tool-bearing turns cross 200,000 estimated tokens.
- `pi-web-access` — web search, page fetching, YouTube/video handling.
- `agent-browser` and `surf-cli` — browser automation options.
- Anthropic document Agent Skills for `docx`, `pdf`, and `xlsx`.
- This repo's own Agent Skills from `tmustier/claude-to-pi`.

If you want plan mode, todos, command approvals, sandboxing, background shells, CRM tools, or a different browser workflow, ask Pi first. There may already be a maintained extension; if not, Pi can usually build a focused one.

### Compaction defaults

This setup installs [`tmustier/pi-auto-compact`](https://github.com/tmustier/pi-auto-compact) with a default threshold of 200,000 estimated tokens. After a tool-bearing turn crosses the threshold, the extension persists Pi's native compaction and continues the active request without adding a user continuation message.

The policy lives in `~/.pi/agent/auto-compact.json`. The previous local post-run and soft-context implementation remains in this repository with a `.disabled` suffix for reference. The setup does not copy or load it.

## Good optional additions

- **Reuse existing skills:** add `~/.claude/skills` or `~/.codex/skills` to Pi settings if those directories exist, or symlink useful skills into `~/.pi/agent/skills/`.
- **Secrets brokering:** consider Infisical / agent-vault-style workflows for sensitive credentials.
- **Isolation:** consider a local QEMU micro-VM / `pi-gondolin` style setup for stronger tool sandboxing.
- **MCP:** keep MCP servers purposeful. Prefer a simple CLI + Agent Skill when that is enough; use MCP for real external execution surfaces.

## Customising for your team

Fork the repo and edit:

- `AGENTS.template.md` — your team conventions, addresses, safety rules, and source-of-truth systems.
- `settings.template.json` — package list, scoped models, and resource paths.
- `prompts/` — reusable workflows.
- `skills/` — team-specific Agent Skills.
- `extensions/` — runtime behaviour, custom tools, commands, UI, or safety gates.

## License

MIT
