#!/usr/bin/env python3
"""Print Spencer's messages from recent transcripts, each after the reply it answered."""

import json
import pathlib
import re
import sys
import time

CURSOR_GLOB = ".cursor/projects/*/agent-transcripts/**/*.jsonl"
CLAUDE_GLOB = ".claude/projects/*/*.jsonl"
SKIP_PROJECT = "dotfiles-worker"
LOOKBACK_S = 24 * 3600
MAX_USER_CHARS = 1500
REPLY_TAIL_CHARS = 400
SUBAGENT_PROMPT = re.compile(r"^\s*(You are\b|Read the full reviewer prompt)")
# Messages Cursor sends in the user's seat after a subagent finishes.
INJECTED_PREFIXES = ("Briefly inform the user", "Perform any necessary follow-up")
USER_QUERY = re.compile(r"<user_query>\s*(.*?)\s*</user_query>", re.DOTALL)
TAG = re.compile(r"<[^>]+>")


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    return "\n".join(
        part.get("text", "") for part in content if part.get("type") == "text"
    )


def cursor_turns(line: dict):
    content = line.get("message", {}).get("content", [])
    text = text_of(content)
    if line.get("role") == "user":
        match = USER_QUERY.search(text)
        return "user", match.group(1) if match else ""
    return "assistant", text


def claude_turns(line: dict):
    if line.get("isSidechain") or line.get("isMeta"):
        return None, ""
    kind = line.get("type")
    if kind not in ("user", "assistant"):
        return None, ""
    content = line.get("message", {}).get("content", "")
    if (
        kind == "user"
        and isinstance(content, list)
        and any(part.get("type") == "tool_result" for part in content)
    ):
        return None, ""
    text = text_of(content)
    if kind == "user" and text.lstrip().startswith("<"):
        return None, ""
    return kind, text


def exchanges(path: pathlib.Path, parse):
    """Yield (agent reply tail, Spencer's message) pairs from one transcript."""
    last_reply = ""
    for raw in path.read_text(errors="replace").splitlines():
        try:
            role, text = parse(json.loads(raw))
        except (json.JSONDecodeError, AttributeError):
            continue
        text = TAG.sub("", text).strip()
        if not text:
            continue
        if role == "assistant":
            last_reply = text
        elif role == "user":
            yield last_reply[-REPLY_TAIL_CHARS:], text


def recent(pattern: str) -> list[pathlib.Path]:
    cutoff = time.time() - LOOKBACK_S
    paths = pathlib.Path.home().glob(pattern)
    return sorted(
        p for p in paths if p.stat().st_mtime >= cutoff and SKIP_PROJECT not in str(p)
    )


def main() -> int:
    sources = [(p, cursor_turns) for p in recent(CURSOR_GLOB)]
    sources += [(p, claude_turns) for p in recent(CLAUDE_GLOB)]
    for path, parse in sources:
        pairs = list(exchanges(path, parse))
        if not pairs or SUBAGENT_PROMPT.match(pairs[0][1]):
            continue
        kept = [
            (r, u)
            for r, u in pairs
            if len(u) <= MAX_USER_CHARS and not u.startswith(INJECTED_PREFIXES)
        ]
        if not kept:
            continue
        print(f"## {path}\n")
        for reply, message in kept:
            if reply:
                print(f"> agent: ...{reply}\n")
            print(f"Spencer: {message}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
