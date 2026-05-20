---
name: todo-audit
description: Create, review, and maintain markdown todo files with absolute dates and checklist status. Use when the user asks to capture tasks, audit outstanding todos, update todo status, or organise reminders.
---

# Todo Audit

Use this skill for file-based todo capture and review.

## Canonical format

Read `todo-format.md` before creating or editing todos. Follow it exactly.

## Rules

- Use absolute dates only: `YYYY-MM-DD`. Do not write "tomorrow", "next week", or similar relative dates.
- Create one file per distinct ask.
- Put related sub-tasks inside the file as a checklist.
- When a todo is completed, change `Status` to `done`; do not delete the todo unless the user explicitly asks.
- If the user gives an ambiguous due date, ask before writing the file.
