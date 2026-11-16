"""Re-run the matrix plus the injected-trailer tolerance case."""

import importlib.util
import pathlib

spec = importlib.util.spec_from_file_location(
    "hook", pathlib.Path.home() / ".cursor" / "hooks" / "no-ai-attribution.py"
)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

INJECTED = '--trailer "Co-authored-by: C' + 'ursor <cursoragent@cursor.com>"'

cases = [
    # (expected, label, command)
    ("allow", "cursor-injected trailer, real message clean", f'git commit {INJECTED} -m "eol: trim the peer-link comments"'),
    ("deny", "injected trailer AND a leaked body line", f'git commit {INJECTED} -m "eol: x" -m "Ge' + 'nerated with Cursor"'),
    ("deny", "hand-written trailer, not the injected form", 'git commit -m "eol: x" --trailer "Co-authored-by: somebot <a@b.c>"'),
    ("deny", "pr body with attribution", 'gh pr create --body "made with cl' + 'aude"'),
    ("allow", "clean pr create", 'gh pr create --title "eol: x" --body "BESS-2455"'),
    ("allow", "clean commit", 'git commit -m "eol: settle cal power points"'),
    ("allow", "audit search", 'git log | rg -i "co-authored-by"'),
]

failures = []
for expected, label, command in cases:
    got = hook._decision(command)["permission"]
    flag = "ok " if got == expected else "FAIL"
    print(f"{flag} {got.upper():5} expect {expected.upper():5} {label}")
    if got != expected:
        failures.append(label)

print()
print("FAILURES:", failures if failures else "none")
