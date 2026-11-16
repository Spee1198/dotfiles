#!/usr/bin/env python3
"""Deny shell commands that write AI attribution into git or GitHub text.

Scans the command itself and any body file it points at. Read-only commands
(rg, grep, gh pr view) are untouched, so auditing for attribution still works.
"""

import json
import re
import sys

# Only the commands that publish text. A search for "co-authored-by" is fine.
WRITE_COMMAND = re.compile(
    r"""(
        git \s+ commit
      | git \s+ tag
      | git \s+ notes
      | gh \s+ pr \s+ (create|edit|comment|review|merge)
      | gh \s+ issue \s+ (create|edit|comment)
      | gh \s+ release \s+ (create|edit)
      | gh \s+ api
    )""",
    re.VERBOSE | re.IGNORECASE,
)

ATTRIBUTION = re.compile(
    r"""(
        co-authored-by
      | generated \s+ (with|by) \b
      | (made|written|created|authored|assisted) \s+ (with|by) \s+
            (cursor|claude|anthropic|copilot|an?\s+ai|ai\b)
      | with \s+ the \s+ help \s+ of \s+ (cursor|claude|ai)
      | claude \s+ code
      | cursor \s+ agent
      | cursor \. (com|sh) \b
      | anthropic \. com
      | noreply@anthropic
      | \U0001F916
    )""",
    re.VERBOSE | re.IGNORECASE,
)

BODY_FILE_ARG = re.compile(r"(?:--body-file|--file|-F)[=\s]+([^\s'\"]+)")

# Cursor injects this into agent git commits. .git/hooks/commit-msg strips it
# before the commit object is written, so denying here only blocks committing.
INJECTED_TRAILER = re.compile(
    r"--trailer\s+[\"']?Co-authored-by:\s*Cursor\s*<[^>]*>[\"']?",
    re.IGNORECASE,
)

MAX_BODY_BYTES = 262_144


def _body_file_text(command: str) -> str:
    """Text of every body file the command points at, empty if unreadable."""
    chunks = []
    for path in BODY_FILE_ARG.findall(command):
        try:
            with open(path, encoding="utf-8", errors="replace") as handle:
                chunks.append(handle.read(MAX_BODY_BYTES))
        except OSError:
            continue
    return "\n".join(chunks)


def _decision(command: str) -> dict:
    if not WRITE_COMMAND.search(command):
        return {"permission": "allow"}
    command = INJECTED_TRAILER.sub("", command)
    hit = ATTRIBUTION.search(command) or ATTRIBUTION.search(_body_file_text(command))
    if hit is None:
        return {"permission": "allow"}
    found = " ".join(hit.group(0).split())
    return {
        "permission": "deny",
        "user_message": (
            f"Blocked a git/GitHub write carrying AI attribution: {found!r}."
        ),
        "agent_message": (
            f"Denied by the no-ai-attribution hook: this command publishes {found!r}. "
            "Rewrite the message, body, or comment with no mention of AI, Cursor, "
            "Claude, or a Co-authored-by trailer, then run it again. Do not work "
            "around this hook."
        ),
    }


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        print(json.dumps({"permission": "allow"}))
        return 0
    print(json.dumps(_decision(payload.get("command") or "")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
