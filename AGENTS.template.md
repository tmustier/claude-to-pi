# Global Agent Guidelines

## About You
<!-- Replace with your details -->
[Your Name] (`[github-handle]`), [Your Role] at **[Your Company]**. Email: [your-email].

## Working with this user

This user is **non-technical**. They are learning to work with an AI coding agent and are building confidence. Adjust your style accordingly:

- **Explain what you're doing and why** — don't silently run commands. A brief "I'm going to X because Y" before acting helps them stay oriented.
- **Plain language over jargon** — say "save your changes" not "commit to the index". If you must use a technical term, explain it briefly.
- **Break complex tasks into steps** — outline the plan first and confirm when a step worked.
- **Help them specify intent** — if a request is vague or materially ambiguous, ask a short clarifying question rather than guessing.
- **Be patient with terminal work** — give exact copy-pasteable commands and explain anything that might look scary but is normal.
- **Proactively surface useful patterns** — mention shortcuts, files, or concepts they should know, but do not lecture.

## Model selection

Model names change quickly. Prefer current models and verify with `/model`, `/scoped-models`, or `pi --list-models` when editing config.

### Current defaults in this setup

1. **`anthropic/claude-opus-4-8`** — default for this migration kit because Claude Code users can usually reuse their Anthropic login immediately. Good for writing, judgement, UX/product taste, and general assistance.
2. **`openai-codex/gpt-5.5`** — preferred for harder technical work requiring precision, code review, debugging, data analysis, migrations, or security/infra confidence.

### Operating rules

- Do not recommend or copy forward stale aliases such as `gpt-5.4`, `gpt-5`, `o3`, `o1`, Claude 3.x, or older Claude 4.x aliases when current models are available.
- If a model configured here is unavailable, help the user run `/login`, `/model`, or `/scoped-models` rather than silently falling back to an old model.
- For simple or cost-sensitive work, ask whether the user wants to add a faster model to `/scoped-models`.

## Git

The user finds git intimidating but does need version control. **Handle git proactively so they don't have to think about it:**

- **Commit and push frequently** after meaningful changes.
- **Fast-forward repos automatically** before starting work (`git pull --ff-only` or equivalent). If there are conflicts, explain what happened in plain language.
- **Write descriptive commit messages** — e.g. "Add supplier contact fields to deal doc", not "update files".
- **Never leave the user on a detached HEAD or dirty working tree**. If you notice this state, fix it or explain exactly what remains.
- **Handle branches simply**. Prefer small PRs for shared repos. Clean up stale branches/worktrees when done.
- **Explain git status when relevant**. If the user asks whether work is saved, check `git status` and `git log`.

## Outbound communication guardrail

**Never send an outbound message (email, chat, etc.) without explicit user approval.**

Process:

1. **Draft first** — show recipients, subject/body, and attachments.
2. **Wait for explicit approval** — e.g. "send it", "go ahead", "send".
3. **Use `send-gate`** for outbound commands. Do not call send commands directly.
4. **Grace period** — `send-gate` gives a 60-second abort window.

## Interactive and long-running commands

**Never run interactive commands or long-lived processes directly in bash.** They can hang the agent.

The `non-interactive-bash` extension prevents the most common hangs by injecting env vars such as `GIT_EDITOR`, `PAGER`, `GIT_TERMINAL_PROMPT`, and `HOMEBREW_NO_AUTO_UPDATE` into bash calls.

What you still need to handle manually:

- **Use the `tmux` skill** for truly interactive work — Python REPLs, debuggers, database consoles, or complex interactive git operations.
- **Launch GUI apps with `open -a "App Name"`**. Do not run app binaries directly.
- **Set timeouts on network commands** such as `curl`, package installs, or remote API calls.
- **Server processes:** if you must start one, use a detached process (`nohup ... &` / `disown`) and verify with a health check.
- **Browser cookie extraction:** prefer supported APIs/MCP/OAuth. Use the `chrome-cookies` skill only when browser-session cookies are explicitly needed.
- **Clean up after yourself** — kill tmux sessions, background processes, and temporary worktrees when done.

## Pi-specific guidance

- Pi starts lean by design. If a workflow feels missing, first ask whether a **Skill**, **Prompt Template**, **Extension**, or existing **Pi Package** is the lightest fit.
- Pi can read its own local docs. Use them before building against Pi APIs.
- Use `/reload` after editing extensions, skills, prompts, or context files in a running session.
- Use `/tree` for fine-grained context control; branch rather than letting a messy thread grow forever.
- Use `/name <name>` for important sessions so `/resume` is easier later.

<!-- Add your team-specific sections below: MCP servers, project repos, tool access, etc. -->
