# Engineering City Lab — phased plan

Status: **Phase 0 reviewed and merged; Phase 1 synthetic question MVP implemented
on 2026-10-24 and awaiting instructor review. Stop at a draft PR.**

Prepared on 2026-10-23 (Asia/Taipei). This project adds Digital Electronics
assignments to the imported Slop New York city. It does not rebuild the city or
continue the maze project's gameplay. `AGENTS.md` contains the binding constraints.

## Baselines and Phase 0 deliverables

| Item | Record |
| --- | --- |
| Imported city baseline | `cca9c12a096951d63fee1d26904c04be0a128cef` — Import Slop New York |
| Imported upstream | `mrdoob/slop-newyork` at `4b899b006120155514aee2e1558b4d14906c87e4` |
| Preparation branch | `docs/phase-0-project-preparation`, branched from that `main` |
| Rules | [AGENTS.md](AGENTS.md) |
| Source inventory, architecture, spawn and five terminal candidates | [docs/architecture.md](docs/architecture.md) |
| Import identity, dependency state and licensing | [docs/upstream.md](docs/upstream.md) |
| Existing tests, actual results and manual regression checklist | [docs/baseline-tests.md](docs/baseline-tests.md) |
| S01–S12 v1/v2 integration boundary | [docs/assignment-compatibility.md](docs/assignment-compatibility.md) |

Phase 0 work completed:

- [x] Inspect all tracked areas: entry/UI, 29 city modules, 13 test files and
  their helper, eight tool scripts, eleven geography/query inputs and notices.
- [x] Trace initialization, rendering, controls, maps, traffic, collision and
  saved-position behavior; identify additive integration points.
- [x] Identify the exact imported upstream commit through Git ancestry and
  verify that only `README-initial.md` differs from its tree.
- [x] Inspect the reference assignment schemas, validators, loader, fixtures
  and related tests at an immutable reference commit, without copying them.
- [x] Create project rules, phased milestones and review records.
- [x] Run baseline tests: **105 passed, 0 failed** after allowing subprocesses.
  Complete syntax checks and local HTTP resource smoke checks also passed.
- [x] Keep imported runtime/data/tests unchanged; implement no educational feature.
- [x] Instructor reviews Phase 0 and explicitly authorizes Phase 1. PR #1 merged
  as `974fddf2feecc96faf6856818f2eb452f83991df`. Feature branch:
  `feature/phase-1-education-mvp`, based on that reviewed main.

Review should cover the fixed-start policy, proposed terminal area, preservation
boundary, four/five-question mapping, no-reset retry policy, reference contract
and validation limits. Physical placements remain a Phase 1 verification task.

## Phase 1 — minimal educational interaction MVP

**Approved scope:** the instructor's 2026-10-24 request supersedes the earlier
placeholder-only Phase 1 plan. Demonstrate approaching a fixed terminal, pressing
X, answering a clearly labeled synthetic question, retrying and retaining passes.
Keep rendering, physics, city systems and Three.js imports unchanged.

1. Capture a Windows 11 Chrome/Edge comparison using the preserved baseline and
   the existing manual checklist. Use a clean browser origin for the default
   spawn, and separately exercise saved-player-state behavior.
2. Add one educational configuration module with an explicit taxi start at
   `(3.6, 0, 410.6)`, heading 0, and five immutable terminal IDs/locations near it.
   Give the educational start precedence over saved city positions without
   clearing unrelated preferences. Do not add resets to normal teleport actions.
3. Survey the proposed sites against actual rendered props, facades, pedestrians,
   traffic and chase/POV views. Freeze adjusted coordinates in configuration;
   use small nonblocking markers under an independent scene group. Do not alter
   the city geometry, road graph or collision data to make room.
4. Add nearest-terminal interaction from active player world position, with
   horizontal distance, height and obstruction checks: walking 3 m, car 18 m,
   bicycle 8 m; car/bicycle speed <= 0.5 m/s. Disable helicopter interaction.
   X ignores repeats, modifiers, typing and other dialogs. Preserve other keys.
5. Implement an accessible question/options/submit/feedback/close dialog using
   five clearly labeled demo questions. Store progress only in memory. A correct
   answer passes only that question; an incorrect answer permits immediate retry
   without changing passes or player position. Reopening preserves completion.
   Show a demo completion message after all five, without an exit requirement.
6. Implement coordinated modal
   input handling. Keep the city safe while interacting; avoid coasting or
   traffic pushing the player through a dialog. Resume without a time-step jump.
   Preserve map/search/teleport/camera/mode behavior outside the dialog.
7. Add focused tests for fixed spawn despite saved state, five stable sites,
   interaction range, altitude, repeated/modifier keys, typing/focus and dialog
   input cleanup, answer/retry/completion and independent mode/teleport behavior.
   First rerun the 105 imported tests; after implementation run all tests and
   practical real-browser checks, distinguishing Linux automation from Windows
   physical verification. Supply local HTTP test instructions and a draft PR.

Exit evidence: visible fixed terminals, repeatable fixed startup, nearest eligible
X interaction, synthetic answer/retry/progress/completion, safe modal pause,
unchanged city features, baseline/new tests and explicit browser limitations.
No S01–S12 loading, v1/v2 port, teacher GUI, videos, Forms, timers or new rendering.
**Open a draft PR and stop for review. Do not merge or begin Phase 2.**

Implementation and review instructions: [docs/phase-1-results.md](docs/phase-1-results.md).
The rendered survey moved Q02 from x = 12 to x = 11 to clear facade occlusion;
all other proposed coordinates remain fixed. No city geometry was changed.

## Phase 2 — assignment contract and session adapter

Requires Phase 1 approval. Review the reference version and reuse/licensing
record before porting validated components.

- Bring over only reviewed v1/v2 schemas, pure validation/rules and synthetic
  contract cases, with source revision and license attribution. Do not port
  maze generation, failure/reset/map-budget or exit logic.
- Add a relative-path manifest allowlist loader and unit selector. Handle empty
  manifests, malformed/missing files, cancellation, stale requests, failed
  switching and subdirectory hosting without destroying the active session.
- Maintain state independently of the city: active unit, active question,
  passed question IDs and validated content. Keep session progress in memory
  unless a later requirement authorizes persistence.
- Map Q01–Q05 to the same five sites for every unit. For a four-question unit,
  keep T05 in place but inactive and exclude it from completion.
- Implement single-label acceptance for both versions. Incorrect answers change
  feedback only; previously passed IDs, player position and fixed sites remain.
- Verify Python/JavaScript/schema parity against the existing reference cases,
  all twelve allowed unit IDs, three/four options, four/five questions and
  explicit version errors. Add tests for every city-specific state rule.

Exit evidence: synthetic units load and validate in v1/v2, retry preserves
progress, failed/cancelled switches preserve the active unit, and unchanged city
regressions pass. **Stop for review.**

## Phase 3 — complete educational interaction

Requires Phase 2 approval.

- Connect the approved synthetic interaction UI to questions/options/feedback
  from the validated unit. Preserve supplied text and option order; use safe DOM APIs.
- Offer the question video and, after a correct answer, optional explanation
  video/text. Open external links only by explicit user action.
- Show progress for the active four/five questions. Unlock the existing unit's
  Google Form once all required IDs pass, wherever the player is. Require no
  exit, maze, countdown or map restriction.
- Confirm a deliberate unit replacement before resetting educational state;
  keep unrelated city controls and preferences intact. No reset on wrong answers.
- Verify dialog accessibility, keyboard cleanup, touch/gamepad coordination,
  safe external links and cancellation. Use synthetic fixtures until the
  instructor explicitly publishes real assignment files.

Exit evidence: complete v1/v2 learner flows and retry/switching checks pass,
with physical Windows review of the unchanged city. **Stop for review.**

## Phase 4 — regression and deployment preparation

Requires Phase 3 approval.

- Run imported tests plus contract/session/browser integration tests. Add a
  documented CI job only within the approved tooling scope.
- Compare initial loading, city visuals, traffic, all travel modes/cameras,
  audio, minimap/full map/search and both teleport paths against the baseline.
  Record browser versions, GPU and results; do not invent FPS targets from HTML
  metadata or cloud CPU measurements.
- Verify static hosting from a subdirectory and public-data privacy boundaries.
  Document dependencies on the existing external CDN/fonts; offline packaging
  and dependency pinning are separate changes requiring review.
- Package source/license/data attribution and an empty public manifest by
  default. Document manual unit-first, manifest-last publication using the
  existing local teacher workflow.

Exit evidence: a reviewable release candidate and reproducible instructions.
Deployment, release publication and integration into `main` require explicit
authorization. Preserve the imported baseline commit and all historical tags.
