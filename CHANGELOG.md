# Changelog

## Unreleased

- Refreshed the repo for current Pi: updated native shortcuts, `/scoped-models`, `/tree`, `/name`, `/reload`, message queue guidance, and the small-by-default setup philosophy.
- Replaced stale model references with `anthropic/claude-opus-4-8` and `openai-codex/gpt-5.5`.
- Slimmed the default package set to core defaults: subagents, MCP adapter, web access, browser automation, document skills, and this repo's Agent Skills.
- Modernized `/onboard`, `/machine-doctor`, startup tips, tmux skill socket naming, and update instructions.
- Removed committed `.pi/extensions` duplicates that could conflict with globally installed extensions when opening this repo in Pi.
- Clarified Pi skill loading during bootstrap and cleaned up stale `claude-to-pi/skills/...` package entries so repo-owned Agent Skills are not loaded as extensions. Thanks @just4masha for the original fix and `todo-audit` skill discovery cleanup in PR #2.
