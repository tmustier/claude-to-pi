# Agent-Friendly Design — Reference

Extended rationale, benchmarks, examples, and source material. Read when you need deeper context on a specific principle or want to cite evidence.

---

## 1. The Agent-Computer Interface (ACI)

Coined by Princeton's SWE-agent team (Yang et al., 2024). The key finding: **the interface given to the agent matters as much as the model itself**. A well-designed ACI improved SWE-bench scores by 50%+ over giving the same model a raw bash shell.

ACI is the agent analog of HCI/UX. Where HCI optimizes for discoverability and forgiveness, ACI optimizes for predictability and defense-in-depth.

The "API" an agent uses is: command surface + help text + output shapes + exit codes. Everything else is noise.

**Source:** arxiv.org/abs/2405.15793

---

## 2. The Knowledge / Execution Split — Evidence

### The GitHub MCP example
The GitHub MCP server consumed ~50,000 tokens of context to teach an agent how to interact with GitHub (later trimmed to ~23,000). A SKILL.md saying "use the `gh` CLI for these operations" achieved the same in ~200 tokens. That's a 100–250× difference.

### David Cramer (Sentry)
"Many MCP servers don't need to exist" — they're either poor API wrappers or replaceable with a skill file.

### The three-layer decision framework
1. **Does the agent need to know something?** → Skill file (markdown, version-controlled)
2. **Does the agent need to do something?** → Tool / MCP / CLI
3. **Does the agent need to know AND do?** → Skill file that references tools

### CompanyOS (Brad Feld, Feb 2026)
Runs an entire company on 12 markdown skill files + 8 MCP servers for execution. The knowledge layer works even if MCP is disconnected — you just copy-paste instead of auto-sending. Skills include: co-comms (email), co-support (Help Scout), co-search (cross-system), co-l10-prep (meeting metrics), co-launch (product launches), co-feedback (user feedback), co-ops (decision log), co-calendar (scheduling).

Each skill follows a 7-section template: frontmatter, when to use, context, process, output format, guardrails, standalone mode.

**Sources:**
- thenewstack.io/skills-vs-mcp-agent-architecture (Mar 2026)
- adventuresinclaude.ai/posts/2026-02-21-running-a-company-on-markdown-files (Feb 2026)
- cra.mr/mcp-skills-and-agents (David Cramer)

---

## 3. CLI Design — Extended Examples

### JSON payloads vs flat flags (Justin Poehnelt, Google Workspace CLI)

```bash
# Human-first: 10 flat flags, can't express nesting
my-cli spreadsheet create --title "Q1 Budget" --locale "en_US" --frozen-rows 1 ...

# Agent-first: one flag, the full API payload — zero translation loss
gws sheets spreadsheets create --json '{
  "properties": {"title": "Q1 Budget", "locale": "en_US"},
  "sheets": [{"properties": {"title": "January", "sheetType": "GRID",
    "gridProperties": {"frozenRowCount": 1, "frozenColumnCount": 2}}}]
}'
```

Practical compromise: support both paths. Use `--output json` or `OUTPUT_FORMAT=json` env var, or default to JSON when stdout isn't a TTY.

### Schema introspection replacing documentation

```bash
gws schema drive.files.list        # Dumps full method signature as machine-readable JSON
gws schema sheets.spreadsheets.create
```

The CLI becomes the canonical source of truth for what the API accepts *right now*, not what docs said six months ago. Uses Google's Discovery Document with dynamic $ref resolution.

### Context window discipline

```bash
# Field masks limit response size
gws drive files list --params '{"fields": "files(id,name,mimeType)"}'

# NDJSON pagination — stream-processable, no buffering
gws drive files list --page-all --output ndjson
```

From gws CONTEXT.md: "Workspace APIs return massive JSON blobs. ALWAYS use field masks when listing or getting resources."

### Input hardening

Agents hallucinate parameter names and values. The CLI must:
- Validate every parameter against the API schema
- Return structured errors with specific field-level messages
- Never silently accept invalid input and produce unexpected behavior

### nibzard's error envelope

```json
{
  "schema_version": "1.0",
  "command": "deploy",
  "status": "failed",
  "run_id": "abc123",
  "data": null,
  "errors": [{
    "class": "auth",
    "code": "TOKEN_EXPIRED",
    "retryable": true,
    "hint": "Re-authenticate with `tool auth refresh`"
  }],
  "warnings": [],
  "metrics": {"duration_ms": 342}
}
```

**Sources:**
- justin.poehnelt.com/posts/rewrite-your-cli-for-ai-agents (Mar 2026)
- nibzard.com/ai-native (Mar 2026)

---

## 4. File Format Benchmarks

### Nested data retrieval (ImprovingAgents.com, Oct 2025)

Tested GPT-5 Nano, Llama 3.2 3B, Gemini 2.5 Flash Lite on 1,000 questions per format using nested Terraform-like config data (6–7 levels deep):

| Format | Accuracy (GPT-5 Nano) | Accuracy (Gemini Flash Lite) | Relative tokens |
|---|---|---|---|
| YAML | **62.1%** | **Best** | ~10% more than Markdown |
| Markdown | 54.3% | Good | **Baseline (most efficient)** |
| JSON | 50.3% | Poor | 51% more than Markdown |
| XML | 44.4% | Worst | 80% more than Markdown |

Key: YAML wins accuracy for nested data, Markdown wins token efficiency. JSON is surprisingly poor under stress. XML worst on both axes.

Note: accuracy was intentionally stressed to 40–60% range to discriminate. Real-world accuracy with normal data sizes approaches 100% for all formats.

### Markdown for web content (Cloudflare, Feb 2026)

Blog post example: 16,180 tokens in HTML → 3,150 in Markdown = **80% reduction**.

Cloudflare launched edge HTML→Markdown conversion via `Accept: text/markdown` content negotiation. Claude Code and OpenCode already send these headers. Response includes `x-markdown-tokens` header for context window budgeting.

### Agent-Flavored Markdown (WSO2, Feb 2026)

Emerging format: YAML frontmatter for config + Markdown body for instructions. This is exactly what SKILL.md and AGENTS.md already use — it's becoming a recognized pattern beyond the agent coding space.

**Sources:**
- improvingagents.com/blog/best-nested-data-format
- blog.cloudflare.com/markdown-for-agents
- wso2.com/library/blogs/introducing-agent-flavored-markdown

---

## 5. Context Infrastructure — The Codified Context Paper

Vasilopoulos (Feb 2026) built a 108,000-line C# system entirely with Claude Code and developed a three-tier context architecture:

### Tier 1: Hot memory (constitution)
- Always loaded at session start
- Conventions, retrieval hooks, orchestration protocols
- Compact, high-signal — analogous to AGENTS.md

### Tier 2: Specialized domain agents
- 19 agents with embedded project-specific knowledge
- Loaded when task matches their domain
- Analogous to Pi skills

### Tier 3: Cold memory (knowledge base)
- 34 on-demand specification documents
- Loaded only when explicitly needed
- Analogous to reference libraries

### Scale metrics (283 sessions)
- 2,801 human prompts
- 1,197 agent invocations
- 16,522 agent turns
- ~26,000 lines of context infrastructure for 108K lines of code

Google Conductor (Feb 2026) for Gemini CLI follows a similar pattern: persistent Markdown with a structured spec-plan-implement workflow.

**Source:** arxiv.org/abs/2602.20478

---

## 6. The ETH Zurich Counter-Study

Gloaguen et al. (Feb 2026) tested AGENTS.md effectiveness on 138 real-world Python tasks across 4 agents (Claude 3.5 Sonnet, Codex GPT-5.2 and 5.1 mini, Qwen Code):

| Condition | Success rate delta | Cost delta |
|---|---|---|
| No context file | Baseline | Baseline |
| LLM-generated file | **−3%** | **+20%** |
| Human-written file | **+4%** | **+19%** |

LLM-generated context files hurt. Human-written files helped marginally but increased cost.

Why: agents followed instructions (ran more tests, read more files, did more grep) but this extra work was often unnecessary for the specific task. Architectural overviews didn't reduce time spent locating files.

**Takeaway:** include only non-inferable information. The signal-to-noise ratio matters more than comprehensiveness.

Developer response was nuanced — many argued the study validates that *good* human-written context works, and that the real lesson is to write focused, non-obvious guidance rather than kitchen-sink files.

**Source:** infoq.com/news/2026/03/agents-context-file-value-review, arxiv.org/pdf/2602.11988

---

## 7. Agentic UX Principles

### Standard Beagle framework (Jul 2025)
When the user is a machine, interface design shifts from visual to semantic:
- Screens → APIs, event streams, machine-readable formats
- Visual hierarchy → Semantic architecture
- Microcopy → Schema documentation
- Label consistency and data integrity become UX concerns

"A mislabeled database field might not confuse a human, but it can halt an AI mid-task."

### AXIS framework (2024–2025)
API-first agent design: applications expose clean APIs that agents call directly. The GUI becomes optional — a human oversight layer, not the primary interface.

### Microsoft's 3 principles (Apr 2025)
1. Keep the human in the loop — calibrate oversight level
2. Make the agent's state legible — what it's doing, planning, unsure about
3. Design for delegation, not automation — human delegates intent, agent handles execution

**Sources:**
- standardbeagle.com/agentic-ux-designing-interfaces-for-agents
- microsoft.design/articles/ux-design-for-agents
- arxiv.org/abs/2409.17140

---

## 8. Making Codebases Agent-Friendly (tedivm, Mar 2026)

"Beyond the Vibes" guide on setting a foundation:

1. **Tests** — the primary feedback loop. Agents need automated verification.
2. **Static analysis** — linters, type checkers, formatters give agents structure.
3. **CI + PR reviews** — automated guardrails catch what agents miss.
4. **Documentation** — focused, non-inferable, not duplicative.
5. **Spec-driven development** — write the spec first, let agents implement.

> "Both AI and standard deterministic computing have their strengths and weaknesses, but when paired together they both perform much better than on their own."

Also recommends: treat AGENTS.md as a living document, use tools like Context7 for platform documentation, integrate issue trackers so agents can read and write tickets.

**Source:** blog.tedivm.com/guides/2026/03/beyond-the-vibes

---

## 9. Anthropic's Agent Skills Design (Oct 2025)

Core design principles from the official Skills framework:

1. **Progressive disclosure** — name/description always loaded, full SKILL.md on demand, reference files only when needed
2. **Skills = directories** — SKILL.md + optional helper files, scripts, references
3. **Scripts for capability gaps** — embed runnable code for things the agent can't do natively
4. **Eval-driven development** — test skills against real scenarios, iterate on evidence

Skill building is like writing an onboarding guide for a new hire: capture the procedural knowledge someone would need to do the job, not the general knowledge they'd already have.

**Source:** anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

---

## Learnings Log

Record project-specific observations and lessons below as they come up.

### Template

```
### YYYY-MM-DD — [short title]
**Context:** what was being built/designed
**Observation:** what happened
**Lesson:** what to do differently
```

<!-- Add new entries below this line -->
