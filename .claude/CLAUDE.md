# Spencer's standing instructions

The rules imported below are the source of truth, shared with Cursor. Edit them
in `~/.cursor/rules/`, never re-state their contents here. Each opens with
three lines of YAML frontmatter that Cursor uses. Ignore it.

<!-- rules:start -->
@~/.claude/rules/personal-code-standards.md
@~/.claude/rules/personal-decide-dont-ask.md
@~/.claude/rules/personal-feedback-inbox.md
@~/.claude/rules/personal-git-and-prs.md
@~/.claude/rules/personal-hil.md
@~/.claude/rules/personal-how-i-work.md
@~/.claude/rules/personal-keep-my-deletions.md
@~/.claude/rules/personal-memory.md
@~/.claude/rules/personal-review-and-reporting.md
@~/.claude/rules/personal-unit-tests.md
@~/.claude/rules/personal-writing-style.md
<!-- rules:end -->

# Claude Code specifics

- One copy of every rule. `~/.cursor/rules/*.mdc` is the source of truth,
  `~/.claude/rules/*.md` are symlinks to it, and the `rules:start` block above
  is generated. Never write rule text into this file.
- `~/.claude/sync-cursor-rules.sh` enforces that, from Claude Code's
  `SessionStart` hook and Cursor's `sessionStart` and `stop` hooks. It deletes
  a real `.md` file that shadows a rule, promotes a Claude-only rule back to
  Cursor as `.mdc`, repoints wrong symlinks, and drops orphans. Run it with
  `--check` to report divergence and exit 1 without touching anything.
- Adding a rule in Cursor needs no other step, but it lands one session late:
  CLAUDE.md is read before the hook rewrites it. Editing an existing rule is
  immediate, since the symlink already points at it.
- Skills are shared with Cursor at `~/.cursor/skills/`. `code-review` and
  `/code-review` mean
  `~/.cursor/skills/multi-model-code-review/SKILL.md`. Read it before
  reviewing.
- `~/.claude/skills/ticket-folder/SKILL.md` is Claude Code's own.
- rw-bess has four clones. `Documents/GitHub/rw-bess` is current. Memory is
  clone-independent at `~/.claude/memory/rw-bess`.
- rw-bess `.gitignore` ignores `.claude/` but not a root `CLAUDE.md`. Never
  create one at the repo root: it would commit personal rules to the team repo.
