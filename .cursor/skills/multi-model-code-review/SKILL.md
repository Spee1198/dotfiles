---
name: multi-model-code-review
description: >-
  Co-review a code change with Claude Opus 5.5 high and GPT 5.6 sol in parallel,
  verify what they find, then report only what is broken. Use when the user says
  code review, /code-review, or co-review on a PR, branch, or local diff.
---

# Co-review (Claude + GPT, fast)

Two reviewers in parallel, the parent verifies their findings, one table back.
Target: reply within 15 minutes. `prompt.md` is the reviewer prompt. `evals.md`
holds past PRs and misses; record any bug a passed PR later shows there.

## Setup, under 3 minutes

- Target: a PR at its head (a stacked PR's base is its base branch), else the
  local diff. Skip drafts. Empty diff: say so and stop.
- Never fetch, merge, or reset in Spencer's checkout. Fetch with
  `--no-write-fetch-head`. One head worktree under `/tmp`, submodule init, `uv
  sync` in each touched package.
- `gh pr checks <n>`. Do not rerun a suite green CI already ran.
- `git merge-tree --write-tree --name-only origin/main <head>` for conflicts.
- Julian PR: apply the review gate in memory first.
- Never touch hardware: no `HW_TYPHOON`, `HW_PACMAN`, `--serial-number`, or
  bench dispatch; `--virtual` on anything that opens CAN. Read-only on GitHub.

## Reviewers

Two `generalPurpose` Task agents, `run_in_background: true`, one turn:
`claude-opus-5-5-high` and `gpt-5.6-sol-medium` (a higher GPT sol slug if
listed). Same `prompt.md`, filled with target, worktree, CI result, and up to
five memory facts that bear on the diff. Model unavailable: run the other alone.

No completeness continuations. Resume one only when the two contradict each
other on a finding. While they run, one line per notification. If Spencer asks
early, give only rows already verified.

## Verify (parent)

Agents propose; the parent owns every row. For each candidate:

1. Rerun the command or probe it rests on. An agent's output is a claim.
2. Check the latest main run of the same surface (nightly, CI job). Same
   failure on main: not a row.
3. Bench or flake claim: read every run on the PR branch. A test that passed
   in any of them is intermittent.
4. Name who sees it break and which run or operator hits it after merge.
   No such path: not a row.

Not a row: PR body, comments, docstrings, missing tests, style, suggestions.
Confirm the head SHA has not moved, then remove the worktree.

## Reply

```text
**<Request changes|Approve with fixes>.** [PR <n>](<url>)

| Severity | Where | Issue | Fix |
|---|---|---|---|
| **Blocking** | `<file:line>` | <who sees what break> | <imperative fix> |

Tested:
- CI: <passed>/<total> checks passed
```

Nothing to fix: `**Approve.** [PR <n>](<url>)` plus one or two sentences on
the mechanism that makes it right, then Tested.

- **Blocking**: merged state is broken. **Major**: a named run or operator
  fails after merge. **Minor**: a real break where nothing fails, such as
  wrong log text or a report figure.
- Issue and Fix: one plain sentence each. Tested: counts the parent saw, at
  most four lines.
- Voice is Spencer's, paste-ready. No model or reviewer names, no hedging, no
  mention of what was dropped or safe.

Post to the PR only on `--comment` or "post it": same table, one or two
sentences per row below it, then the fix. No auto-fix unless asked.
