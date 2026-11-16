#!/usr/bin/env python3
"""Surface style violations in commit messages, PR bodies, and staged code.

Returns "ask" rather than "deny": the objective rules (subject shape, length,
em dashes, filler words) are worth a look before publishing, but style is a
judgment call and must never hard-block work. Attribution is a separate hook
and does deny.
"""

import json
import re
import shlex
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass

WRITE_COMMAND = re.compile(
    r"""(
        git \s+ commit
      | gh \s+ pr \s+ (create|edit|comment)
      | gh \s+ issue \s+ (create|edit|comment)
    )""",
    re.VERBOSE | re.IGNORECASE,
)

# From the writing-style and commit rules. Stems, so suffixes are caught.
FILLER = re.compile(
    r"""\b(
        comprehensive | robust | seamless(ly)? | leverag(e|es|ing|ed)
      | streamlin(e|es|ing|ed) | enhanc(e|es|ing|ed|ement|ements)
      | ensur(e|es|ing|ed) | properly | successfully | simply | actually
      | really | very | just
    )\b""",
    re.VERBOSE | re.IGNORECASE,
)

# CI's own rule from .github/pr-title-checker-config.json.
SUBJECT_SHAPE = re.compile(r"^.+: \w.+$")
SUBJECT_MAX = 75

TICKET_IN_SUBJECT = re.compile(r"\b[A-Z]{2,}-\d+\b")

# Em dash, en dash, and `--` used as punctuation. Command flags do not match:
# `--body` has no space or word char on both sides of the dashes.
DASH = re.compile(r"[\u2014\u2013]|(?<=\s)--(?=\s)|(?<=\w)--(?=\w)")

FENCED_BLOCK = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE = re.compile(r"`[^`]*`")
URL = re.compile(r"https?://\S+")


def _prose(text: str) -> str:
    """Text with code spans and URLs blanked, so `ensure_ready()` is not filler."""
    for pattern in (FENCED_BLOCK, INLINE_CODE, URL):
        text = pattern.sub(" ", text)
    return text


def _message_parts(command: str) -> tuple[list[str], bool]:
    """Values of -m/--body/--title in the command, and whether parsing worked."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        return [], False
    flags = {"-m", "--message", "-b", "--body", "-t", "--title"}
    parts = []
    for index, token in enumerate(tokens[:-1]):
        if token in flags:
            parts.append(tokens[index + 1])
        elif token.startswith(("--body=", "--title=", "--message=")):
            parts.append(token.split("=", 1)[1])
    return parts, True


def _subject_findings(subject: str) -> list[str]:
    findings = []
    if len(subject) > SUBJECT_MAX:
        findings.append(f"subject is {len(subject)} chars, limit is {SUBJECT_MAX}")
    if not SUBJECT_SHAPE.match(subject):
        findings.append("subject does not match CI's 'prefix: summary' shape")
    if TICKET_IN_SUBJECT.search(subject):
        findings.append("subject carries a ticket designator")
    return findings


COMMENT_BLOCK_MAX = 3
COMMENT_LINE = re.compile(r"^\+\s*(#|//)")
GIT_DIFF_TIMEOUT_S = 5

CODE_SUFFIXES = (".py", ".c", ".h", ".ts", ".tsx", ".js", ".rs", ".sh")
# Project keys only: a generic [A-Z]+-\d+ also hits UTF-8 and SHA-256.
TICKET_KEY = re.compile(r"\b(BESS|BDV)-\d+\b")
WIDE_DASH = re.compile(r"[\u2014\u2013]")
COMMENT_TEXT = re.compile(r"(?:#|//)(.*)$")
BANNER_COMMENT = re.compile(r"^\s*(#|//)\s*[-=*#]{5,}")
INLINE_WAIT = re.compile(r"\b(sleep\(\s*\d|timeout(_s)?\s*=\s*\d)")
NEW_TEST = re.compile(r"^\s*(async\s+)?def test_")
# Tests in these trees are the feature itself, not coverage added on the side.
BENCH_TEST_DIRS = ("test/tests/hil/", "test/tests/eol/", "test/tests/sil/")


def _is_test_file(path: str) -> bool:
    return "tests/" in path or path.rsplit("/", 1)[-1].startswith("test_")


def _is_unit_test_file(path: str) -> bool:
    return _is_test_file(path) and not path.startswith(BENCH_TEST_DIRS)


def _any_file(path: str) -> bool:
    return True


def _source_file(path: str) -> bool:
    return not _is_test_file(path)


@dataclass(frozen=True)
class LineCheck:
    label: str
    matches: Callable[[str], bool]
    applies_to: Callable[[str], bool]


def _comment_has_dash(line: str) -> bool:
    comment = COMMENT_TEXT.search(line)
    return bool(comment and DASH.search(comment.group(1)))


LINE_CHECKS = (
    LineCheck("ticket key in code", lambda line: bool(TICKET_KEY.search(line)), _any_file),
    LineCheck("em dash in code", lambda line: bool(WIDE_DASH.search(line)), _any_file),
    LineCheck("-- in a comment", _comment_has_dash, _any_file),
    LineCheck("banner comment", lambda line: bool(BANNER_COMMENT.match(line)), _any_file),
    LineCheck(
        "inline sleep or timeout literal",
        lambda line: bool(INLINE_WAIT.search(line)),
        _source_file,
    ),
    LineCheck(
        "new unit test, only when asked",
        lambda line: bool(NEW_TEST.match(line)),
        _is_unit_test_file,
    ),
)


def _staged_diff(cwd: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", cwd, "diff", "--cached", "-U0"],
            capture_output=True,
            text=True,
            timeout=GIT_DIFF_TIMEOUT_S,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return result.stdout


def _staged_code_findings(cwd: str) -> list[str]:
    """One finding per check that an added code line trips, naming the files."""
    hits: dict[str, set[str]] = {}
    path = ""
    for line in _staged_diff(cwd).splitlines():
        if line.startswith("+++ "):
            path = line[6:] if line.startswith("+++ b/") else ""
            continue
        if not path.endswith(CODE_SUFFIXES) or not line.startswith("+"):
            continue
        for check in LINE_CHECKS:
            if check.applies_to(path) and check.matches(line[1:]):
                hits.setdefault(check.label, set()).add(path)
    return [f"{label} in {', '.join(sorted(paths))}" for label, paths in hits.items()]


def _long_comment_blocks(cwd: str) -> list[str]:
    """Files whose staged diff adds a comment run over the ceiling."""
    offenders = []
    path = ""
    run = 0
    for line in _staged_diff(cwd).splitlines():
        if line.startswith("+++ b/"):
            path, run = line[6:], 0
        elif COMMENT_LINE.match(line):
            run += 1
            if run == COMMENT_BLOCK_MAX + 1:
                offenders.append(path)
        else:
            run = 0
    return sorted(set(offenders))


def _findings(command: str, cwd: str = "") -> list[str]:
    parts, parsed = _message_parts(command)
    text = "\n".join(parts) if parsed and parts else command
    prose = _prose(text)

    findings = []
    if DASH.search(prose):
        findings.append("em dash or --")
    words = sorted({match.group(0).lower() for match in FILLER.finditer(prose)})
    if words:
        findings.append("filler words: " + ", ".join(words))
    is_commit = re.search(r"git\s+commit", command, re.IGNORECASE)
    if parsed and parts and is_commit:
        subject = parts[0].strip().splitlines()[0] if parts[0].strip() else ""
        if subject and not subject.lower().startswith(("merge ", "revert ", "fixup!")):
            findings.extend(_subject_findings(subject))
    if is_commit and cwd:
        offenders = _long_comment_blocks(cwd)
        if offenders:
            findings.append(
                f"comment block over {COMMENT_BLOCK_MAX} lines in "
                + ", ".join(offenders)
            )
        findings.extend(_staged_code_findings(cwd))
    return findings


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        print(json.dumps({"permission": "allow"}))
        return 0

    command = payload.get("command") or ""
    if not WRITE_COMMAND.search(command):
        print(json.dumps({"permission": "allow"}))
        return 0

    findings = _findings(command, payload.get("cwd") or "")
    if not findings:
        print(json.dumps({"permission": "allow"}))
        return 0

    joined = "; ".join(findings)
    print(
        json.dumps(
            {
                "permission": "ask",
                "user_message": f"Style check on this git/GitHub text: {joined}.",
                "agent_message": (
                    f"Style hook flagged this text: {joined}. Rewrite it to match the "
                    "writing rules before running it again, or continue if the flag "
                    "is wrong."
                ),
            }
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
