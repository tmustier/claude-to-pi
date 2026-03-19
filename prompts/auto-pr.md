---
description: Implement work via PRs with AI review + merge loop
---
Task/context: $@

If Task/context is empty or unclear, ask for clarification and stop.

Please read all you need, then implement and open a PR, following this process:

1. Implement the work on a branch and open a PR.
2. Run a review using the `pr-reviewer` subagent (see below). Pass it the diff and PR context — it will return structured findings.
3. Post the review output as a PR comment:
   ```bash
   gh pr comment <pr_number> --body-file <review_output_file>
   ```
4. Evaluate the review findings. Apply fixes for anything P0-P2 that you agree with — don't apply changes mindlessly, and skip findings that are wrong or don't apply.
5. If you made fixes, push and re-review (subagent again). One re-review maximum — don't loop endlessly.
6. Merge when green (resolve merge conflicts as needed).

### Running the review subagent

Use the `pr-reviewer` subagent with the diff piped in. Example:

```
subagent(agent: "pr-reviewer", task: "Review PR #<number> against <base_branch>.\n\n<diff>\n$(git diff origin/<base_branch>...HEAD)\n</diff>")
```

The subagent returns markdown findings. Write them to a temp file and post via `gh pr comment`.

### After merge — quick self-check

Briefly consider: is there a clearly better implementation or obvious refactoring opportunity? If yes and it's material (not cosmetic), open a follow-up PR. If not, move on. Do not re-review follow-up PRs unless the changes are substantial.

### General guidelines

- We are aiming for clear, simple structure & code that are easy to understand and maintain. Robust but not overly verbose or defensive.
- There is ongoing parallel work in this repo — avoid interfering. Use an isolated worktree when appropriate, and fast-forward to the latest before starting each PR.
- If you need to split implementation across multiple PRs, repeat the process for each.
- When done, clean up your workspace at a sensible point, taking care not to overwrite ongoing work from others.
