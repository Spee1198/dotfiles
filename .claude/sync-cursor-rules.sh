#!/bin/sh
# Keep Cursor and Claude Code on one copy of every rule.
#
# ~/.cursor/rules/*.mdc is the source of truth. ~/.claude/rules/*.md are
# symlinks to it, and CLAUDE.md's rules:start block is generated from them.
# Cursor loads only .mdc. Claude Code skips .mdc imports and does not auto-load
# ~/.claude/rules, so both halves are required.
# https://github.com/anthropics/claude-code/issues/18518
#
# Pass --check to report divergence and exit 1 without changing anything.
exec python3 "$HOME/.claude/sync_cursor_rules.py" "$@"
