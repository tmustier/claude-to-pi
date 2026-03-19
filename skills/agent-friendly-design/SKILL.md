---
name: agent-friendly-design
description: Design things that AI agents can operate effectively — CLIs, tools, file formats, codebases, context layers, skills, visual assets, and any interface where agents are the primary or frequent consumer. Use when building a CLI for agents to use, structuring a codebase or repo for AI-assisted development, choosing file formats for agent-readable content, designing MCP tools or skills, creating agent-operable assets (HTML templates, markdown-driven workflows), setting up context infrastructure (AGENTS.md, SKILL.md, progressive disclosure), or making any existing system more agent-friendly. Also use when the user asks about agent DX, agent UX, or how to make something easy for agents to work with.
license: MIT
---

# Agent-Friendly Design

Design interfaces, formats, codebases, and systems that agents can operate effectively. This skill encodes the principles — read `reference.md` for deeper rationale, benchmarks, and source material.

## Use alongside other skills

Use this skill to decide the **agent-operability pattern** and architecture, then pair it with more implementation-specific skills when needed:

- **`skill-creator`** — when packaging a reusable Pi skill after deciding the structure, trigger, context split, and supporting references/scripts
- **`extending-pi`** — when deciding whether the right solution is a skill, extension, prompt template, theme, package, or other Pi-native mechanism
- **`mcp-builder`** — when the answer is to build a real MCP server or tool surface, not just capture workflow knowledge in Markdown
- **Artifact / implementation skills** such as **`frontend-design`**, **`pptx`**, **`docx`**, **`pdf`**, or **`xlsx`** — when producing the final human-facing asset after choosing an agent-operable source format and workflow

## Core mental model

Every agent task is either a **knowledge** problem or an **execution** problem. Getting this distinction wrong is the #1 source of waste.

| Problem type | Solution | Format | Example |
|---|---|---|---|
| Agent needs to **know** something | Markdown file (skill, spec, guide) | `.md` | "Use squash merges, run tests before push" |
| Agent needs to **do** something | Tool, CLI, API, MCP server | JSON I/O | Query a database, send an email, create an issue |
| Both | Skill file that references tools | `.md` → CLI/API | Skill explains workflow, calls `gog`/`gh`/`gws` for execution |

Don't build runtime infrastructure for knowledge problems. Don't encode institutional knowledge inside tool schemas.

## File format selection

Pick based on what the agent needs to do with it:

| Use case | Format | Why |
|---|---|---|
| Instructions, docs, workflow guides | **Markdown** | Most token-efficient, native to LLM training, human-readable |
| Structured config, nested data | **YAML** | Best accuracy on nested data retrieval (benchmark-proven) |
| API I/O, tool responses | **JSON** | Agents expect it; keep payloads lean with field masks |
| Visual assets agents produce/edit | **HTML** | Agents can generate, edit, and preview; no binary formats |
| Tabular data | **CSV/TSV** or **YAML** | Avoid XLSX as working format; convert at boundaries |

Avoid XML (80% more tokens than Markdown for same content), binary formats (DOCX, PPTX) as primary working formats, and deeply nested JSON when YAML or Markdown would suffice.

Token cost reference: HTML→Markdown conversion yields ~80% token reduction (Cloudflare data).

## CLI design for agents

When building a CLI that agents will use:

### Output
- **Default to JSON** (or JSON when stdout isn't a TTY)
- Use a **consistent envelope** across all commands:
  ```json
  {"status": "succeeded", "data": {...}, "errors": [], "warnings": []}
  ```
- No spinners, progress bars, or emoji in machine mode
- NDJSON for streaming/pagination

### Input
- Support **raw JSON payloads** as first-class input (`--json '{...}'`), not just flat flags
- Validate all input against the schema — never silently accept invalid input
- Return structured errors with field-level messages

### Errors
Every failure should include:
- **Error class**: input / auth / network / rate-limit / not-found
- **Retryable**: true or false
- **Hint**: bounded guidance on what to try next

### Discoverability
- `--help` is a **contract**: usage, args, flags, examples, output modes, exit codes
- Expose **schema introspection** (`schema <method>`) so agents self-serve at runtime
- Keep `--help` concise — every token competes with agent reasoning

### Safety
- `--non-interactive` / `--yes` by default in agent mode
- Token/key auth over browser OAuth redirects
- **Idempotency keys** so the same operation can run twice safely
- Split **validate** from **run** when possible (`task validate` vs `task run`)

### Recovery
- Provide `doctor` / diagnostic commands
- Support bounded retries with `--max-retries` and `--timeout-ms`
- Make `replay` cheap for debugging failures

## Context infrastructure

### Progressive disclosure (3 tiers)

Structure context so agents load only what they need:

1. **Hot memory** — always loaded (compact, high-signal)
   - AGENTS.md / CLAUDE.md: project conventions, build commands, key decisions
   - Skill frontmatter: name + description only

2. **Warm memory** — loaded on demand when task matches
   - Full SKILL.md bodies
   - Domain-specific guides
   - Architecture decision records

3. **Cold memory** — loaded only when explicitly needed
   - Reference docs, API schemas, long specifications
   - Historical data, changelog archives

### What to include in context files

**Include** (non-inferable information):
- Custom build commands and tooling
- Project-specific conventions that deviate from defaults
- Domain knowledge unique to the project
- Which tools to use and when

**Exclude** (the agent already knows or can discover):
- Architectural overviews discoverable from the code
- Generic best practices the model was trained on
- Information that LLM-generation would produce anyway

Human-written context > LLM-generated context. LLM-generated context files have been shown to *degrade* agent performance.

## Codebase structure for agents

- **Tests are the primary feedback loop** — agents need automated verification, not human review
- **Static analysis** (linters, type checkers, formatters) gives agents guardrails to work within
- **CI pipelines** catch what agents miss — treat them as the safety net
- **Spec-driven development** — write the spec (markdown), let the agent implement
- **Small, focused files** > monolithic files — easier for agents to read, edit, and reason about
- **Consistent naming** — agents navigate by pattern matching; be predictable

## Designing tools and skills

When creating something agents will use as a tool:

- **Name clearly** — the name is the first (sometimes only) signal an agent gets
- **Describe in terms of user intent** — "Use when the user asks to..." not "This module provides..."
- **Return meaningful context** — not just success/failure, but what happened and what to do next
- **Namespace boundaries** — keep each tool's scope clear and non-overlapping
- **Token-budget awareness** — large tool responses eat into reasoning capacity; trim or paginate
- **Prompt-engineer descriptions** — usage examples, parameter docs, and "when to use" guidance in the tool description itself

## Agent-operable visual assets

When creating visual materials (one-pagers, decks, marketing assets) that agents should be able to edit:

- Use **HTML + CSS** as the source format — agents read, edit, and generate it natively
- Inline styles or single-file CSS for self-contained portability
- Avoid design tools (Figma, Canva) as the source of truth — they're opaque to agents
- Store in version control alongside content
- Render to PDF/PNG at the boundary when humans need final output
- Keep content and presentation separable where practical

## Checklist

When making something agent-friendly, verify:

- [ ] Knowledge vs execution: is this the right layer?
- [ ] Format: markdown for knowledge, JSON for I/O, HTML for visual?
- [ ] Output: structured, consistent, lean?
- [ ] Errors: classified, retryable flag, recovery hint?
- [ ] Discoverability: schema introspection or complete `--help`?
- [ ] Context budget: field masks, progressive disclosure, no bloat?
- [ ] Safety: non-interactive, idempotent, validated input?
- [ ] Recovery: can the agent retry, diagnose, and replay?
- [ ] Tests: does automated verification exist?
- [ ] Human oversight: approval gates for irreversible actions?
