---
name: weekly-update
description: >-
  Draft Spencer's weekly update or 1:1 notes from merged PRs, open PRs, commits,
  and Jira, then draft the "what was done" Jira description updates for tickets whose PRs
  merged. Use when he asks for his weekly update, 1:1 notes, standup prep, what
  he did last week, or to update his in-progress tickets from GitHub.
---

# Weekly update

Gather, draft the update, draft the Jira descriptions, then the monthly folder check.
Nothing is posted. Jira writes wait for his explicit go on each ticket.

## 1. Window

Start date is the last 1:1 date he gives or pastes. Otherwise the Monday of last
week. End is today. Note any OoO days he mentions; do not guess them.

## 2. Gather, in parallel

```zsh
cd ~/Documents/GitHub/rw-bess && git fetch -q origin
gh pr list --author @me --state merged --search "merged:>=START" \
  --json number,title,mergedAt,url,headRefName,body --limit 100
gh pr list --author @me --state open \
  --json number,title,isDraft,reviewDecision,url,headRefName,mergeable
gh pr list --author @me --repo redwoodmaterials/rw-test-infrastructure \
  --state all --search "updated:>=START" --json number,title,state,url
gh pr list --search "reviewed-by:@me -author:@me updated:>=START" \
  --state all --json number,title,author,url
git log origin/main --author=Spencer --since=START --no-merges --format="%h %ad %s" --date=short
git worktree list   # then `git -C <path> status --short` on each for uncommitted work
```

Infra PRs and uncommitted worktree work count as work in the window.

Jira, cloudId `redwoodmaterialsinc.atlassian.net`, through
`searchJiraIssuesUsingJql`:

```
assignee = currentUser() AND (updated >= "START" OR statusCategory != Done)
ORDER BY status, updated DESC
```

Drop any ticket not assigned to him. Merged PRs with no ticket still count.

Ticket key comes from the branch (`spencer/BESS-3631-...`), then the PR body's last
line. A PR with no ticket gets listed under "No ticket" so he can file one.

## 3. Draft the update

Areas, in this order, and only the ones with work in the window:

| Area | PR prefixes |
|---|---|
| HIL | `hil:`, `ci:` touching HIL workflows |
| Pacman End-of-Line Tester | `eol:` |
| Firmware Flashing Station | `preflash:` |
| Pack Screener | screener work, usually Jira only |
| Other | everything else, including `ci:` and reviews given |

Template, matching his 10/01 notes:

```
MM/DD/YYYY

Spencer's Weekly Update

OoO: <only if he said so>

HIL
	• <what changed for the bench or the operator, in plain words> (BESS-XXXX)
	• <...> (BESS-XXXX) - In Review

Pacman End-of-Line Tester
	• <...>

TLDR:
	• <one line, the two or three things that mattered>

Next Week:
	• <In Progress tickets, next tickets in the HIL build order>

Something I want in the future after HIL + 1.5:
	• <carry forward his previous bullets verbatim>

Zahra Notes:
```

Rules for the bullets:

- Lead with the effect, not the code: "30 kW discharge cut from 60 s to 10 s, saves
  about 50 s per unit", not "change dwell constant".
- Status from the source: `isDraft` or review state for In Review, Jira status
  for the rest. Never write a closed or merged date. An open PR is In Review
  under its area, never Next Week.
- Changes requested is stale when commits were pushed after that review.
- One bullet per outcome, grouping every PR and ticket behind it. Never one
  bullet per PR. Ticket keys in parentheses, no links unless he asks.
- Condensing merges lines, never drops one. Recount every number after an edit.
- Say what changed against what existed before. Read the diff, not the title.
- Only what happened or what he committed to. A finished deck is not a given
  talk, and a plan's proposal is not his commitment. No asks for his boss.
- Numbers only from a PR body, commit, Jira, or a bench run. Never invent cycle time,
  throughput, or dollars. Measured and expected stay separate.
- Reviews he gave count. One line under Other: "Reviewed N PRs (#a, #b)",
  with N filled from the reviewed-by query.
- No em dashes.

## 4. Draft the Jira description updates

For every ticket whose PR merged in the window and whose description does not
yet say what merged, draft an addition to the description, never a comment:

```
Merged in #NNNN on M/D.
<What changed, two or three declarative lines naming files or registers.>
<What was verified: bench run link, CI run, or "bench run pending".>
```

HIL fault tickets also need the close checklist from `personal-hil.mdc`. Fill each
from the source and mark the rest "not recorded":

- Fault injection method: the row's inject lever in `test/tests/hil/test_*_fault_injection.py`
- Trip and clear thresholds, with units: the row or `pack_config.h`
- Timing requirements: `timeout_s` and `min_latency_s` on the row
- Key implementation choices and assumptions: PR body Decisions section

List the drafts with ticket key and suggested transition (Done or In Review).
Post or transition only the ones he approves.

## 5. Monthly, first update of the month only

Compare tickets with a merged PR this month against folder names under
`~/Library/CloudStorage/OneDrive-SharedLibraries-OneDrive-RedwoodMaterials/Projects Folder BESS 2026/`.
List the tickets with no folder and the folders whose ticket closed this month.
Fill gaps with the `ticket-folder` skill only when he says to.
