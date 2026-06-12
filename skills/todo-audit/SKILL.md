---
name: todo-audit
description: Audit and reconcile Thomas's todo list against all active data sources — calendar, email, customer deal docs, deal tracker spreadsheet, and any future sources. Use when Thomas asks to "review my todos", "what's outstanding", "todo audit", "anything I'm missing", "check my follow-ups", "what's stale", or as part of a Monday morning / Friday EOD review. Also use when he asks about overdue items, missed follow-ups, or wants a pipeline hygiene check.
---

# Todo Audit

Audit and reconcile `~/todo/` against calendar, email, and deal pipeline.

## Todo format

See [todo-format.md](./todo-format.md) for the file format used in `~/todo/`.

## Procedure

1. Read all files in `~/todo/` to get current todos
2. Pull recent calendar events (`gog calendar list --days 14`)
3. Filter for external calls (ignore internal Nexcade-only meetings, standups, 1:1s)
4. Cross-reference against sent emails for follow-ups
5. Flag any gaps: external calls with no follow-up, overdue items, stale todos
6. Report findings with recommended actions
