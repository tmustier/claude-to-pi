---
name: customer-intel
description: Process sales call recordings into structured customer intelligence. Use when the user asks to process a call transcript, create or update a deal doc, add to the playbook or glossary, or do any work involving call transcripts, deal qualification, or sales reference material.
---

# Customer Intel (Template)

Process sales calls into structured customer intelligence: cleaned transcripts, deal qualification docs, playbook entries, and glossary terms.

**This is a starter template.** Customise the repo structure, deal doc template, and workflow to match your team's sales process.

## Suggested repo structure

Create a private repo for your team (e.g., `your-org/customers`):

```
customers/
├── _templates/deal-doc.md       # Your deal qualification template (MEDDPICC, BANT, etc.)
├── _reference/
│   ├── playbook.md              # Sales patterns, objections & responses
│   └── glossary.md              # Industry-specific terms
├── <customer>/
│   ├── <date>-<description>.md  # Cleaned transcript(s)
│   ├── deal.md                  # Deal qualification doc
│   └── changelog.md             # What changed and why
```

## Workflow: processing a new call

### 1. Pull the transcript

Get the transcript from your meeting recording tool (e.g., Granola, Gong, Otter.ai, Fireflies). Ask Pi: "process my call with [customer]" — it will search your connected meeting tools.

### 2. Clean the transcript

- Fix speaker labels (identify who said what)
- Remove filler words and false starts
- Preserve exact quotes for important statements
- Add section headers for major topic changes

### 3. Update the deal doc

Using your deal qualification framework (MEDDPICC, BANT, SPICED, etc.):
- Extract and update qualification criteria from the conversation
- Note what's confirmed vs. assumed
- Flag gaps that need follow-up

### 4. Update the playbook

If the call revealed:
- A new objection pattern → add to playbook with the response that worked
- A new competitive mention → add to competitive intel section
- A new industry term → add to glossary

### 5. Commit and push

Changes should be committed and pushed immediately so teammates have the latest intel.

## Customisation

To set this up for your team:

1. Create a private repo with the structure above
2. Write your deal doc template in `_templates/deal-doc.md`
3. Start your playbook in `_reference/playbook.md`
4. Add this skill to your Pi setup
5. Edit the skill to reference your specific repo path, meeting tools, and CRM
