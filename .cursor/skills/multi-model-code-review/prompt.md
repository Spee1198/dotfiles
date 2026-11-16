# Reviewer prompt

The parent fills the angle-bracket fields and sends this to both agents.

```text
Find what this change breaks after merge. Report only what you can prove.
Hard limit: 10 minutes. Stop and report when you hit it.

Worktree: <path>, submodule and venv synced
Target: <PR url or diff>
Intent: <one line>
CI: <gh pr checks summary>
Repo facts: <up to five memory facts that bear on this diff>

How:
- Read the diff, then the callers on origin/main. Most bugs sit in a caller,
  a teardown, or a firmware fact outside the diff.
- Treat the PR body and comments as claims to test.
- Run code for runtime claims: a throwaway probe in /tmp/review-<tag>/,
  `PYTHONPATH=. uv run --locked` from the package dir. Never edit the worktree.
- Before calling something broken, check whether origin/main already behaves
  the same way. If it does, drop it.
- Never touch hardware (no HW_TYPHOON, HW_PACMAN, --serial-number, bench
  dispatch; --virtual on CAN). Read-only on GitHub. No subagents.

Output, nothing else:

Findings, most severe first, or `Nothing to fix.`:
### <BLOCKER|SHIPS BROKEN>: <title>
Evidence: <file:line and the command you ran>
Who breaks: <run or operator, and when it next runs>
Fix: <one line>

Unverified (one line each, with the run that would settle it), or `None.`
```
