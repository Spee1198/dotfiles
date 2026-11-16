# Evals

Past reviews with a known right answer. After editing `SKILL.md` or
`prompt.md`, run `/code-review <PR>` on two or three of these and compare.
A changed verdict means the edit broke an earlier lesson.

## PR 2308: hil: exclude slow HIL tests from the default test run

Merged 2026-09-15. The diff added `-m "not slow"` to addopts.

- Review head `61456de59` against base `b596956ba`. Later commit
  `27e0090901` fixed the finding, so the final head has it only in part.
- Expected: one `SHIPS BROKEN`. Run commands that pass no `-m` stop doing
  what their text says. `BENCH-RUNBOOK.md` and the `test_droop_v5.py`
  docstring collect nothing (4 deselected), as does
  `test_droop_debug_v5.py` (3 deselected). The `test_hil_harness.py`
  "full suite" command drops all 7 droop tests.
- On the day, GPT found the droop part and Claude returned `Nothing to
  fix.` On 2026-10-06, Opus 5.5 found all four. GPT 5.6 Sol and Muse 1.3
  each found the three droop commands and missed `test_hil_harness.py`.
  Muse's first launch failed with `resource_exhausted`.

## PR 1928: hil: restore nightly discharge tests after derating threshold change

Merged 2026-08-24.

- Review head `6589fd4fb3` against base `38ad5c73d`. Later commit
  `ef9a72a675` scoped the xfail to `v5-2pac-standalone`.
- On 2026-10-06, GPT 5.6 Sol and Muse 1.3 both found it.
- Expected: `SHIPS BROKEN` on the droop-step xfail, which is wider than its
  own reason text.
- On the day, the parent dropped it because tonight's nightly stayed green.
  That drop was wrong: a later run gets muted.

## PR 2568: hil: fail the session when the model upload or start fails

Merged 2026-09-29.

- Expected: the `Exercised:` line shows the new tests run on base and
  failing there.
- On the day, both agents returned `Nothing to fix.` with no record of what
  they ran, and nobody checked the new tests against base.

## PR 1875: test: bump rw-test-infrastructure past accidental branch pin

Merged 2026-08-17 (PDT). A submodule pin correction.

- Expected: `Safe to merge`, with one `SHIPS BROKEN` item.
  `node/am263x/tool/benchtop/GUI/fault_log.py:202` calls
  `fetch_fault_capture` without the `getattr` guard that
  `dcdc_bringup_gui.py` uses. Anyone running the bringup GUI from source
  hits it on their next bench session. The packaged GUI picks it up at the
  next release-bundle build.
- The verdict turned on trace question 2, what runs the caller. Renamed CAN
  signals, constants, model files, and DBC entries carry no `def` line, so
  walk the `--stat` list as well.
- Behavior that existed only on the bad pin is not a regression.

## PR 2882: eol: Attempt to stop bus PSU internal faults during reboots

Open as of 2026-10-19.

- Review head `5f4345340` against base `11ac92ccb`.
- Expected: one `SHIPS BROKEN`. The PR body says each re-enable "returns
  with the bus at voltage". `restore_bus_psu`, `power_cycle_bus` and
  `dut_hardware` discard the `False` from
  `set_voltage(..., wait=True, timeout=BUS_RAMP_TIMEOUT_S)`, then log the
  bus as restored.
- On the day, GPT found it. The parent dropped it because main never
  waited, and Claude returned `Nothing to fix.` That drop was wrong.
- Expected drop: an unverified slew readback in `_configure_bus_psu`. The
  stand log reads back 2.0 s, and the PR states the slew is only logged.

## PR 2894: eol: End a failing run at the end of its section

Open as of 2026-10-19.

- Review head `239db55a4`.
- Expected: two `SHIPS BROKEN`. `test/eol/section_stop.py:22` raises after
  session_finish, so fixture teardown runs inside the GUI's 5 s SIGKILL
  window. `test/eol/pytest_plugin.py:344` counts a teardown failure as an
  error while the row stays PASSED, so it is counted twice.
- On the day, each reviewer found one of the two. The parent confirmed both
  with the real plugin, base `(2,0,passed,Aborted,Pass)` against head
  `(1,1,passed,Error,Pass)`.
- Expected edge-case rows: teardown ordering against the GUI kill, and a
  teardown failure after a passing call.

## Misses

Bugs found after a clean review. Add one entry per bug: PR, reviewed head,
what escaped, and the gate that dropped it or missed it.

- PR 3307, head 90227cd, 2026-11-12. Not an escape: two false rows. A Major
  (walks stop at 1405 V and 1397 V) and a Minor (make marks strict) went out
  before checking the main nightly, which already XFAILs those walks, or
  older branch runs, where the charge walk XPASSed twice. Missed by Merge
  step 3. The review also took 35 minutes: head and base full suites
  repeated green CI, the matrix had 22 rows, and a candidate went out early.

## Output format

- 2026-09-03: wanted the short fix list.
- 2026-09-15: wanted the verdict table, and no row for a change with no
  behavior difference.
- 2026-10-19: wanted exhaustive reviews. The reply now adds Suspected,
  edge-case coverage, and hardware gaps under the verdict table.
- 2026-10-19, later: "only wanna know the broken things". Reviewers still work
  every row, but the reply drops safe rows, Suspected, hardware gaps, and the
  `Exercised:` line.
