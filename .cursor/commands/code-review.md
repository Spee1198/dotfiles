---
description: Co-review via Claude Opus 5.5 high + GPT 5.6 Sol in parallel, parent-verified, reply in 15 minutes
---

Follow `~/.cursor/skills/multi-model-code-review/SKILL.md`.

Target: the PR, branch, or diff in the user message (else current branch / local diff).

Return the skill's final reply: one verdict line, one table of the things
that need fixing, and the Tested counts. Do not drop a named ship surface to make the first pass
look clean.
