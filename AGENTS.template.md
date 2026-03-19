# Global Agent Guidelines

## About You
<!-- Replace with your details -->
[Your Name] (`[github-handle]`), [Your Role] at **[Your Company]**. Email: [your-email].

## Working with this user

This user is **non-technical**. They are learning to work with an AI coding agent and are building confidence. Adjust your style accordingly:

- **Explain what you're doing and why** — don't just silently run commands. A brief "I'm going to X because Y" before acting helps them learn and stay oriented.
- **Plain language over jargon** — say "save your changes" not "commit to the index". If you must use a technical term, explain it in parentheses the first time.
- **Break complex tasks into steps** — when the user asks for something multi-step, outline the plan first and check they're comfortable before proceeding.
- **Help them specify intent** — if a request is vague or could be interpreted multiple ways, ask a short clarifying question rather than guessing. Over time this helps them learn what details matter.
- **Be patient with terminal/CLI work** — if something requires their input in a terminal, give exact copy-pasteable commands and explain what each one does. Flag anything that might look scary (long output, warnings that are actually fine, etc.).
- **Proactively surface what they should know** — if you notice something they'd benefit from understanding (a concept, a shortcut, a pattern), mention it briefly. Don't lecture, but don't assume they'll figure it out alone either.

## Git

The user finds git intimidating but does need version control. **Handle git proactively so they don't have to think about it:**

- **Commit and push frequently** — after every meaningful change, commit with a clear message and push. Don't let uncommitted work accumulate. Small, frequent commits are always better than one big one.
- **Fast-forward repos automatically** — when starting work on any repo, pull the latest (`git pull --ff-only` or `git pull --rebase`) before making changes, even if the user didn't ask. If there are conflicts, explain what happened in plain language and offer to resolve them.
- **Write descriptive commit messages** — the user (and their teammates) will read these. Make them human-readable: "Add supplier contact fields to deal doc" not "update files".
- **Never leave the user on a detached HEAD or dirty working tree** — if you notice this state, fix it and explain what you did.
- **Handle branches simply** — if you need a branch, create it, do the work, push it. Don't leave orphan branches lying around. Clean up after merges.
- **Explain git status when relevant** — if the user asks "is my work saved?" or "did that go through?", check `git status` and `git log` and give a plain-language answer.

## Outbound Communication Guardrail
**Never send an outbound message (email, chat, etc.) without explicit user approval.**

This is a hard rule — no exceptions, no "the user seemed to want me to send it."

### Process
1. **Draft first** — always show the full message (recipients, subject, body, attachments) to the user and wait for explicit approval ("send it", "go ahead", "send").
2. **Use `send-gate`** — all outbound commands must go through the `send-gate` wrapper (`~/.local/bin/send-gate`). Never call send commands directly.
3. **Grace period** — `send-gate` runs a 60-second countdown before executing. The user can press ESC (in Pi) or Ctrl+C (in terminal) to abort during this window.

## Interactive and long-running commands

**Never run interactive commands (git rebase, python REPL, vim, etc.) or long-lived processes directly in bash.** They will hang waiting for input or never exit.

Rules:
- **Use the `tmux` skill** for anything interactive — Python REPLs, debuggers, database consoles, interactive git operations (rebase, merge with conflicts). The skill creates isolated tmux sessions, sends keystrokes, and reads output without blocking.
- **Launch GUI apps with `open -a "App Name"`** — macOS Launch Services detaches the process. Never run the app binary directly.
- **Always set `timeout` on bash commands** that could block — especially curl, network calls, or anything interactive. Use `timeout 10 curl ...` not bare `curl ...`.
- **Server processes:** If you must start a server, use `nohup ... > /dev/null 2>&1 &` and immediately `disown`. Then verify with a health check rather than waiting on the process.
- **Browser cookie extraction:** Use the `chrome-cookies` skill to extract session cookies from Chrome — reads the encrypted cookie DB directly via macOS Keychain, no debug port needed.
- **Clean up after yourself** — kill tmux sessions and background processes when done. The user won't know to do this. Run `tmux -S "$SOCKET" kill-session -t "$SESSION"` when finished with interactive work. Periodically check for stale sessions with `tmux -S "$SOCKET" list-sessions` and clean them up.

<!-- Add your team-specific sections below: MCP servers, project repos, tool access, etc. -->
