#!/usr/bin/env python3
"""Cursor hook: keep ~/.claude/rules symlinked to ~/.cursor/rules.

Cursor hooks must print JSON, so the sync output is swallowed. Run
~/.claude/sync-cursor-rules.sh --check by hand to see divergence.
"""

import json
import pathlib
import subprocess
import sys

SYNC = pathlib.Path.home() / ".claude" / "sync_cursor_rules.py"

if SYNC.exists():
    try:
        subprocess.run(
            [sys.executable, str(SYNC)],
            capture_output=True,
            timeout=10,
            check=False,
        )
    except subprocess.SubprocessError:
        pass  # noqa: S110, a rules sync must never block the agent

print(json.dumps({}))
