"""Matrix for the git-text-style hook."""

import importlib.util
import pathlib
import subprocess
import tempfile

spec = importlib.util.spec_from_file_location(
    "style", pathlib.Path.home() / ".cursor" / "hooks" / "git-text-style.py"
)
style = importlib.util.module_from_spec(spec)
spec.loader.exec_module(style)

HEREDOC = (
    "gh pr create --draft --title \"eol: abort sooner\" --body \"$(cat <<'EOF'\n"
    "{body}\n"
    "EOF\n"
    ')"'
)

cases = [
    ([], "clean commit", 'git commit -m "eol: trim the peer-link comments to the facts"'),
    ([], "clean pr body", 'gh pr create --title "eol: abort sooner" --body "The check sits after the Ready loop."'),
    (["filler"], "filler in commit", 'git commit -m "eol: ensure the robust peer check works properly"'),
    (["em dash"], "em dash in body", 'gh pr create --body "The link is dead \u2014 abort now."'),
    (["em dash"], "en dash in body", 'gh pr create --body "Wait 2 \u2013 4 seconds."'),
    (["em dash"], "spaced double dash", 'gh pr create --body "The link is dead -- abort now."'),
    (["em dash"], "tight double dash", 'git commit -m "eol: full timeout--a shared deadline starves it"'),
    ([], "command flags are not dashes", 'gh pr create --draft --title "eol: x" --body "Clean text." --base main'),
    ([], "double dash pathspec on commit", 'git commit -m "eol: clean subject here" -- test/eol/constants.py'),
    ([], "flag inside backticks in body", 'gh pr create --body "Run `git diff -U0 -- path` first."'),
    (["ticket"], "ticket in subject", 'git commit -m "eol: BESS-2455 abort on dead peer"'),
    (["75"], "subject too long", 'git commit -m "eol: ' + "x" * 80 + '"'),
    (["shape"], "no prefix", 'git commit -m "made the peer link abort sooner"'),
    ([], "merge commit exempt", 'git commit -m "Merge branch main into spencer/BESS-2455"'),
    ([], "backticked ensure is code", 'gh pr create --body "Calls `ensure_ready()` before the wait."'),
    ([], "url with just in it", 'gh pr create --body "See https://example.com/just/a/path for the log."'),
    ([], "read-only untouched", "gh pr view 2012 --json body"),
    ([], "unrelated shell", "uv run pytest tests/unit/"),
    ([], "heredoc body, clean", HEREDOC.format(body="The Ready wait samples f038.\n\nBESS-2455")),
    (["em dash"], "heredoc body, em dash", HEREDOC.format(body="The link is dead \u2014 abort now.")),
    (["filler"], "heredoc body, filler", HEREDOC.format(body="This will ensure a robust abort.")),
]

failures = []
for expect_substrings, label, command in cases:
    findings = style._findings(command) if style.WRITE_COMMAND.search(command) else []
    joined = "; ".join(findings)
    if expect_substrings:
        ok = all(s.lower() in joined.lower() for s in expect_substrings)
    else:
        ok = not findings
    print(f"{'ok  ' if ok else 'FAIL'} {label:30} -> {joined or '(clean)'}")
    if not ok:
        failures.append(label)


def _staged_repo(source: str) -> str:
    """A temp repo with source staged, for the comment-block check."""
    path = tempfile.mkdtemp()
    for args in (["init", "-q"], ["config", "user.email", "a@b.c"], ["config", "user.name", "t"]):
        subprocess.run(["git", "-C", path, *args], check=True, capture_output=True)
    (pathlib.Path(path) / "mod.py").write_text(source)
    subprocess.run(["git", "-C", path, "add", "mod.py"], check=True, capture_output=True)
    return path


four_line_block = _staged_repo(
    "# one fact\n# two fact\n# three fact\n# four fact\nX = 1\n"
)
three_line_block = _staged_repo("# one fact\n# two fact\n# three fact\nX = 1\n")
spread_out = _staged_repo(
    "# one\nA = 1\n# two\nB = 2\n# three\nC = 3\n# four\nD = 4\n"
)

for expected, label, cwd in [
    (True, "four-line comment block flagged", four_line_block),
    (False, "three-line block is the ceiling", three_line_block),
    (False, "separate one-line comments fine", spread_out),
]:
    got = bool(style._long_comment_blocks(cwd))
    ok = got == expected
    print(f"{'ok  ' if ok else 'FAIL'} {label:30} -> flagged={got}")
    if not ok:
        failures.append(label)

print()
print("FAILURES:", failures if failures else "none")
