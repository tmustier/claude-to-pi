# Changelog

## Unreleased

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
