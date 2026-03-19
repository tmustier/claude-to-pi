# Todo

One file per todo. Filename: `YYYY-MM-DD_slug.md` (date = due date).

## Format

```markdown
# Title

| Field       | Value            |
|-------------|------------------|
| Status      | open / done      |
| Due         | YYYY-MM-DD       |
| Reminder    | YYYY-MM-DD       |
| Requested by| Name             |
| Created     | YYYY-MM-DD       |

## Details

What needs to happen.

## Checklist

- [ ] Step 1
- [ ] Step 2
```

## Rules

- All dates are absolute (no "tomorrow", "next week").
- One file per distinct ask. Related sub-tasks go as a checklist within the file.
- When a todo is done, change status to `done`.
