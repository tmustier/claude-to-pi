# agent-friendly-design

A Pi skill for designing things AI agents can operate effectively — CLIs, tools, file formats, codebases, context layers, visual assets, and any interface where agents are a primary consumer.

## What it covers

- **Knowledge vs execution split** — when to use markdown skill files vs tools/CLIs/MCP
- **CLI design for agents** — structured output, JSON input, schema introspection, error contracts, recovery patterns
- **File format selection** — markdown for instructions, YAML for config, JSON for I/O, HTML for visual assets
- **Context infrastructure** — progressive disclosure, what to include (and exclude) in AGENTS.md/SKILL.md
- **Codebase structure** — tests, static analysis, spec-driven development
- **Agent-operable visual assets** — HTML as source of truth for materials agents need to edit

## When it triggers

Building a CLI, tool, or skill for agents. Structuring a codebase or repo for AI-assisted development. Choosing file formats for agent-readable content. Making an existing system more agent-friendly. Creating visual assets agents should be able to edit.

## Use alongside other skills

Use this skill to choose the right agent-operability pattern, then pair it with:

- `skill-creator` for packaging a reusable Pi skill
- `extending-pi` for choosing between Pi-native extension mechanisms
- `mcp-builder` when you actually need to build an MCP server
- `frontend-design`, `pptx`, `docx`, `pdf`, or `xlsx` when producing the final artifact after settling on the agent-friendly source format and workflow

## Structure

```
agent-friendly-design/
├── SKILL.md       # Principles and checklists (loaded when skill triggers)
├── reference.md   # Evidence, benchmarks, examples, source links, learnings log
├── README.md      # This file
└── LICENSE
```

## Sources

Synthesised from 19 sources (2024–2026) including SWE-agent (Princeton), Anthropic's Agent Skills, the Codified Context paper, Cloudflare's Markdown for Agents, ETH Zurich's AGENTS.md study, CompanyOS, and practitioners building agent-first CLIs. Full citations in `reference.md`.

## License

MIT
