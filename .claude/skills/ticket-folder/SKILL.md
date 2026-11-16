---
name: ticket-folder
description: Create or update Spencer's per-ticket performance-review folder (explainer/impact SVGs + portfolio overview) in OneDrive "Projects Folder BESS 2026". Use when starting work on a Jira ticket, hitting a milestone (implemented, PR merged, bench validated), or when asked to update the review folder. Args: ticket key (e.g. BESS-2412), optional status hint.
---

# Per-ticket performance review folder

Maintain the `Projects Folder BESS 2026` folder under OneDrive Documents. This is Spencer's
end-of-year review packet. One subfolder per Jira ticket he works (BESS-* and BDV-* both count).

On macOS the folder is at the OneDrive **root**, not under `Documents/`:

```
~/Library/CloudStorage/OneDrive-RedwoodMaterials/Projects Folder BESS 2026/
```

The Windows path in older notes was under `Documents\`, and following that on the Mac
creates a second empty folder of the same name that OneDrive happily syncs. That happened
on 2026-09-03 and silently swallowed a session's writes until 09-08. Before writing, glob
`~/Library/CloudStorage/OneDrive*/Projects Folder BESS*` and pick the one holding the
ticket subfolders. If two candidates exist, the populated one wins and the empty one is
the decoy; delete it rather than merging into it. If OneDrive is not synced, say so and
stop rather than writing to a made-up path.

## Folder naming

Since 2026-09-11 folders are named `<Area> - <TICKET> - <short summary>`, so Finder groups
them by subject rather than by ticket number. `_tools/rename-manifest.csv` holds the mapping
and reverses it. Areas in use: `Commissioning Tool`, `EOL Cal`, `EOL Firmware`, `EOL Harness`,
`EOL MES`, `EOL Operator UI`, `EOL Peer Link`, `EOL Power`, `EOL Reporting`, `Preflash Station`.
Reuse an existing area before inventing one.

Files inside keep the bare `<TICKET>-*` prefix. `_tools/build_flows.py` and `check_flows.py`
locate a folder by globbing `*<TICKET>*`, so writing to `<TICKET>/` directly creates an empty
twin beside the real one.

## Steps

1. Fetch the ticket from Jira (Atlassian MCP, cloudId `redwoodmaterialsinc.atlassian.net`) for summary, status, priority, assignee. If Jira is unreachable, proceed from session context and say so.
2. Glob `*<TICKET>*` for the folder. Read existing SVGs before editing so status lines and footers get refreshed, not duplicated.
3. Create or update `<TICKET>-explainer.svg`: the problem, before/after flow or key findings, engineering notes, stat tiles. Status text must be honest: "scoped, To Do" / "in progress" / "implemented, bench pending" / "merged". Never inflate.
4. Create `<TICKET>-impact.svg` ONLY when payoff is quantifiable, and lead with KPI tiles (seconds/unit saved, faults/day attacked, rows of new MES evidence, tests added, false-pass holes closed). Every number must be traceable to the ticket, logs, or session work; never invent throughput or dollar figures.
5. Create `<TICKET>-flow.svg` whenever the change moves data or control through the system: a self-contained animated diagram, one node per component or step, SMIL `<animate>`/`<animateMotion>` so it plays on open with no JavaScript, the off-happy-path exits drawn as red boxes, and a one-line caption of the overall flow at the bottom. Declare `xmlns:xlink` and give `<mpath>` both `href` and `xlink:href` so it animates in Quick Look as well as a browser.
6. Create `<TICKET>-bench-test-plan.md` for anything Spencer will run on the stand: numbered cases with the setup, the action, what to watch in the GUI, what to check in MES or the logs, and a closing "not covered here" section. Write it alongside the code, not after.
7. Add a further markdown notes file only for cross-repo work (submodule sequencing etc.).
8. Update `Overall Stats/_2026-portfolio-overview.md`: the ticket's table row (status + impact columns), the "Updated YYYY-MM-DD" line, and the theme paragraph if the ticket opens a new category. Keep the "Numbers worth quoting" bullets consistent with the new status. It lives in `Overall Stats/`, not the folder root; every review-level document belongs there and only ticket folders and `_tools/` sit beside it.

## SVG house style (match existing files in the folder)

- 1300px wide viewBox, height as needed; background `#f9f9f7`
- cards `#fcfcfb` stroke `#e1e0d9`, rx 8; blue action/change boxes `#cde2fb`/`#2a78d6`; green good `#e7f5e7`/`#0ca30c`; red problem/failure `#fbe7e7`/`#d03b3b`
- ink `#0b0b0b` headline / `#52514e` body / `#898781` fine print
- title 26px bold, subtitle 14px, card heads 16px bold, body 13px, fine print 12px, KPI numbers 26px bold
- KPI stat tiles: put them near the top on impact SVGs
- footer bottom-right, 11px `#898781`: `TICKET &#183; status &#183; context &#183; YYYY-MM-DD`
- escape entities (`&#183;` for the dot, `&#8594;` for arrows); no em dashes anywhere, use commas/colons/parens
- system-ui font stack

## Rules

- Honest status always; unstarted work is "scoped, To Do".
- Refresh footer/overview dates whenever touching a file.
- KPIs quantify process improvement; prefer measured over estimated, and label estimates ("~20 s expected").
- Spencer runs bench validation personally; never claim bench-validated until he has.
- Render every SVG and look at it before calling it done: `qlmanage -t -s 1300 -o /tmp/svgcheck <file>.svg`, then read the PNG. Well-formed XML still ships labels that overflow onto neighbouring boxes and sentences left unfinished across `<text>` lines.
