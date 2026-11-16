"""Keep ~/.claude/rules symlinked to ~/.cursor/rules and CLAUDE.md's imports current.

Run with --check to report divergence and exit 1 without changing anything.
"""

import pathlib
import sys

SRC = pathlib.Path.home() / ".cursor" / "rules"
DST = pathlib.Path.home() / ".claude" / "rules"
CLAUDE_MD = pathlib.Path.home() / ".claude" / "CLAUDE.md"
START, END = "<!-- rules:start -->", "<!-- rules:end -->"

FRONTMATTER = "---\ndescription: {name}\nalwaysApply: true\n---\n\n"


def promote(stray: pathlib.Path, fixes: list[str], check: bool) -> None:
    """Move a real .md file in ~/.claude/rules back to Cursor as the source."""
    target = SRC / f"{stray.stem}.mdc"
    fixes.append(f"promote {stray.name} to {target}")
    if check:
        return
    body = stray.read_text()
    if not body.startswith("---"):
        body = FRONTMATTER.format(name=stray.stem) + body
    target.write_text(body)
    stray.unlink()


def relink(link: pathlib.Path, target: pathlib.Path, fixes: list[str], check: bool) -> None:
    fixes.append(f"relink {link.name} to {target.name}")
    if check:
        return
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(target)


def drop(entry: pathlib.Path, reason: str, fixes: list[str], check: bool) -> None:
    fixes.append(f"{reason} {entry.name}")
    if not check:
        entry.unlink()


def sync_links(check: bool) -> list[str]:
    fixes: list[str] = []
    DST.mkdir(parents=True, exist_ok=True)
    for entry in sorted(DST.iterdir()):
        if entry.suffix != ".md":
            continue
        source = SRC / f"{entry.stem}.mdc"
        if not entry.is_symlink():
            # A real file here is a second copy, the thing that diverges.
            if source.exists():
                drop(entry, "delete duplicate of", fixes, check)
            else:
                promote(entry, fixes, check)
        elif not source.exists():
            drop(entry, "remove orphan link", fixes, check)
        elif not entry.exists() or entry.resolve() != source.resolve():
            relink(entry, source, fixes, check)

    for source in sorted(SRC.glob("*.mdc")):
        link = DST / f"{source.stem}.md"
        if not link.is_symlink() and not link.exists():
            fixes.append(f"link {link.name}")
            if not check:
                link.symlink_to(source)
    return fixes


def sync_imports(check: bool) -> list[str]:
    if not CLAUDE_MD.exists():
        return []
    text = CLAUDE_MD.read_text()
    if START not in text or END not in text:
        return [f"CLAUDE.md is missing the {START} block, imports cannot be generated"]
    # ~/ keeps the imports valid under any username.
    imports = "\n".join(f"@~/{p.relative_to(pathlib.Path.home())}" for p in sorted(DST.glob("*.md")))
    head, _, rest = text.partition(START)
    _, _, tail = rest.partition(END)
    new = f"{head}{START}\n{imports}\n{END}{tail}"
    if new == text:
        return []
    if not check:
        CLAUDE_MD.write_text(new)
    return ["regenerate the CLAUDE.md import block"]


def main() -> int:
    check = "--check" in sys.argv
    if not SRC.is_dir():
        return 0
    fixes = sync_links(check) + sync_imports(check)
    if not fixes:
        if check:
            print(f"rules in sync: {len(list(DST.glob('*.md')))} files")
        return 0
    verb = "divergence" if check else "repaired"
    print(f"{verb}: " + "; ".join(fixes), file=sys.stderr if check else sys.stdout)
    return 1 if check else 0


if __name__ == "__main__":
    raise SystemExit(main())
