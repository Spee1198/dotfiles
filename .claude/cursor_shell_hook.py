#!/usr/bin/env python3
"""Run a Cursor beforeShellExecution hook as a Claude Code PreToolUse Bash hook.
Usage: cursor_shell_hook.py <cursor hook script> [--fail-closed]
"""

import json
import pathlib
import subprocess
import sys

CURSOR_HOOK_TIMEOUT_S = 10.0
FAIL_CLOSED_FLAG = "--fail-closed"


def _cursor_decision(cursor_hook: str, payload: dict) -> dict:
    request = {
        "command": (payload.get("tool_input") or {}).get("command") or "",
        "cwd": payload.get("cwd") or "",
    }
    result = subprocess.run(
        [sys.executable, cursor_hook],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=CURSOR_HOOK_TIMEOUT_S,
        check=True,
    )
    return json.loads(result.stdout)


def main() -> int:
    cursor_hook = sys.argv[1]
    is_fail_closed = FAIL_CLOSED_FLAG in sys.argv[2:]
    try:
        decision = _cursor_decision(cursor_hook, json.load(sys.stdin))
    except (OSError, ValueError, subprocess.SubprocessError) as err:
        name = pathlib.Path(cursor_hook).name
        if not is_fail_closed:
            print(f"{name} failed, allowing: {err}", file=sys.stderr)
            return 0
        decision = {"permission": "deny", "agent_message": f"{name} failed: {err}"}

    permission = decision.get("permission")
    # Emitting "allow" would bypass Claude Code's own permission prompts.
    if permission not in ("deny", "ask"):
        return 0
    message_key = "agent_message" if permission == "deny" else "user_message"
    output = {
        "hookEventName": "PreToolUse",
        "permissionDecision": permission,
        "permissionDecisionReason": decision.get(message_key) or "",
    }
    print(json.dumps({"hookSpecificOutput": output}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
