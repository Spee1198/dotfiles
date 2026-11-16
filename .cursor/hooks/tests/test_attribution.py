"""Deny/allow matrix for the no-ai-attribution hook."""

import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "hook", pathlib.Path.home() / ".cursor" / "hooks" / "no-ai-attribution.py"
)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

MUST_DENY = [
    'gh pr create --title "x: y" --body "Generated with C' + 'ursor"',
    'git commit -m "eol: thing" -m "Co-Authored-By: C' + "ursor <noreply@cursor.com>\"",
    'gh pr comment 2012 --body "made with cl' + 'aude"',
    'gh issue create --body "\U0001f916 fixed"',
    'gh pr edit 2012 --body "see https://curs' + 'or.com for details"',
    'gh pr create --body "written by an AI"',
    'gh release create v1 --notes "authored by cl' + 'aude code"',
    'gh api repos/o/r/issues/1/comments -f body="ge' + 'nerated by cursor agent"',
]

MUST_ALLOW = [
    'gh pr create --title "eol: abort sooner" --body "BESS-2455 fix"',
    'git commit -m "eol: settle cal power points on convergence"',
    'git log | rg -i "co-authored-by|generated with|cursor"',
    "gh pr view 2012 --json body",
    'rg -n "cursor" test/',
    'python3 -c "cur = conn.cursor()"',
    "uv run pytest tests/unit/",
    'git commit -m "gui: keep the text cursor in the serial field"',
    "gh pr list --search 'cursor'",
]

failures = []
for command in MUST_DENY:
    got = hook._decision(command)["permission"]
    print(f"{got.upper():5} expect DENY   {command[:62]}")
    if got != "deny":
        failures.append(("should deny", command))

for command in MUST_ALLOW:
    got = hook._decision(command)["permission"]
    print(f"{got.upper():5} expect ALLOW  {command[:62]}")
    if got != "allow":
        failures.append(("should allow", command))

body = pathlib.Path("/tmp/hook_attr_body.txt")
body.write_text("Real body text.\n\nCo-authored-by: someone\n")
got = hook._decision(f"gh pr create --body-file {body}")["permission"]
print(f"{got.upper():5} expect DENY   body-file carrying the trailer")
if got != "deny":
    failures.append(("should deny", "body-file"))

body.write_text("A clean PR body about peer links.\n")
got = hook._decision(f"gh pr create --body-file {body}")["permission"]
print(f"{got.upper():5} expect ALLOW  clean body-file")
if got != "allow":
    failures.append(("should allow", "clean body-file"))

got = hook._decision("gh pr create --body-file /tmp/does-not-exist-xyz")["permission"]
print(f"{got.upper():5} expect ALLOW  missing body-file does not wedge the tool")
if got != "allow":
    failures.append(("should allow", "missing body-file"))

print()
print("FAILURES:", failures if failures else "none")
