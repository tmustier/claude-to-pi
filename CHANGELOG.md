# Changelog

## Unreleased

- Added optional shell extras (`shell/zshrc.claude-to-pi`, sourced from `~/.zshrc`): zsh-autosuggestions with the history + completion strategy, a guarded `compinit`, and the `yolo` alias ported from Claude Code to Pi (`pi --approve`).
- Added cmux Pi session hook installation (`cmux hooks pi install --yes`) to setup and `/machine-doctor`, plus an optional setup-health check. Without the hooks cmux infers Pi session↔pane bindings from the newest session file per cwd and can duplicate or swap same-cwd Pi tabs when restoring sessions after a crash.

- Added a trusted, manifest-driven `setup-health` runner with command, version, file, package, symlink, safe runtime, quick, live, JSON, and multi-manifest checks; integrated it with onboarding and `/machine-doctor`.
- Updated the bundled Chrome-cookie helper to a self-contained `uv` runtime with label-boundary domain matching and regression coverage.
- Added the `papercut` CLI, Pi-aware metadata capture extension, optional deduplicated GitHub inbox submission, explicit `/papercuts-review` prompt, agent safety policy, setup/doctor integration, and tests for sanitized append-only workflow-friction notes.
- Refreshed the repo for current Pi: updated native shortcuts, `/scoped-models`, `/tree`, `/name`, `/reload`, message queue guidance, and the small-by-default setup philosophy.
- Replaced stale model references with `anthropic/claude-opus-4-8` and `openai-codex/gpt-5.6-sol`.
- Clarified isolated-worktree use, the email-only approval gate, internal versus external messaging, and background-first browser automation.
- Slimmed the default package set to core defaults: subagents, MCP adapter, web access, browser automation, document skills, and this repo's Agent Skills.
- Modernized `/onboard`, `/machine-doctor`, startup tips, tmux skill socket naming, and update instructions.
- Removed committed `.pi/extensions` duplicates that could conflict with globally installed extensions when opening this repo in Pi.
- Clarified Pi skill loading during bootstrap and cleaned up stale `claude-to-pi/skills/...` package entries so repo-owned Agent Skills are not loaded as extensions. Thanks @just4masha for the original fix and `todo-audit` skill discovery cleanup in PR #2.
- Added model/context compaction safeguards: post-run default compaction at 120k tokens plus Claude-only soft context compaction around 200k tokens during long tool loops.
- Replaced the local compaction layers with `tmustier/pi-auto-compact@v0.1.1`, using persisted native compaction at a 200k-token default threshold.
- Updated `tmustier/pi-auto-compact` to v0.1.2 so UI extensions can read the effective active-model threshold.
