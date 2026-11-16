# PRD: premise check before a BLOCKER

Date: 2026-10-20. Status: draft for review. Not applied to `SKILL.md` or
`prompt.md`.

## Problem

On PR 2911 the GPT reviewer called the bringup HV check a BLOCKER for every
unit. A second pass found it holds only for 30 kW, and only if a blank board
can reach EOL. Both 40 kW paths flash blank halves in `dut_hardware` before
bringup. The bad-calibration half of the finding had no evidence. The
Reachable gate passed because one path existed, not because every claimed
path did.

## Change

Add a premise check to Merge step 4 in `SKILL.md`, run on every BLOCKER
before it reaches the table:

1. Name the input that triggers it, for example a board with only a
   bootloader.
2. Trace each mode or path to the changed line, on `origin/main`. Note any
   earlier step that already handles the input.
3. Read how neighboring code treats the same input. `test_aux_power.py`
   only warns on a missing ADC frame.
4. Split a finding with two triggers into two rows and score each.
5. Scope the Why cell to the paths that reach it.
6. If reachability rests on a floor fact the repo cannot answer, name the
   fact in the row. The row stays BLOCKER until that fact is answered.

Add to the Reachable gate in `prompt.md`: "every path the finding claims,
not one."

## Eval

Add PR 2911 to `evals.md`, head `02f47ca81`. Expected: BLOCKER scoped to
30 kW, conditional on blank boards reaching EOL. The bad-calibration
trigger is dropped.

## Open

- Whether step 6 keeps the row as BLOCKER or moves it to Suspected.
