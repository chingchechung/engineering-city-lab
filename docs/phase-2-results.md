# Phase 2 — assignment data integration

Prepared 2026-10-24 (Asia/Taipei). Implementation branch:
`feature/phase-2-assignment-integration`, from verified main
**43f4b2660d11e56c091df89888df7b02e9726a70**. GitHub confirmed PR #2 was merged,
including `c2a93e6`, before this branch or implementation was created.

Subsequent review: PR #3 was merged as
`1a362c95fb073b7652028ba47388185936d1cf02` on 2026-10-24 (Asia/Taipei).
The instructor reports **9/9 Windows 11 Phase 2 acceptance checks passed**.
This is instructor-reported evidence; no browser versions, GPU measurements or
FPS were supplied. The historical automated results below remain separate.

The instructor reports **7/7 Windows 11 manual acceptance checks passed** for
Phase 1/1.1. This is instructor-reported evidence, separate from Linux cloud
automation. Browser versions, GPU measurements and FPS were not supplied.

## Result and scope

The unchanged reference v1/v2 validator now feeds a manifest-only loader, a small
assignment selector and an independent in-memory session. The existing five
terminals and question dialog can exercise validated units. Demo Mode remains
the default. The committed `assignments/manifest.json` is empty and no public
unit JSON is committed. Synthetic examples exist only under test paths.

The Phase 1.1 coordinates, radii, X interaction, stationary/obstruction checks,
ground switching, helicopter independence, Return to Start, map/preset teleports
and original city systems are preserved. There is no new renderer, dependency,
physics, city geometry, course publication, teacher UI, server-side tracking,
video/explanation/Form presentation or Phase 3 work.

## Data and state boundaries

- Exactly S01–S12 can be named by the version-1 manifest. No Sxx filename is
  probed before selection from a validated allowlist. Relative URLs work beneath
  the module's hosting directory, including nested Apache/GitHub Pages paths.
- V1 keeps four options and `correctOption`. V2 keeps three/four options and
  distinct `correctOptions`. The learner selects one radio answer; any accepted
  v2 label passes. Versions are never converted, and option/language order stays.
- The native-module bridge wraps byte-identical reference rules/validator files.
  Original normalization and ordered path/code/message objects are retained.
  UI errors summarize the first three issues, like the reference loader; complete
  issues remain in the loader result. See [reuse and notices](assignment-reuse.md).
- Opening the selector owns the existing pause/input/focus gate. Simulation
  pauses while rendering continues; city shortcuts and Return are blocked.
  Close/Escape/Cancel restores control and suppresses keys held through closing.
- Every replacement, including reloading the same unit or leaving Demo Mode,
  requires confirmation. The old unit/progress remains active while loading.
  Only a fully validated replacement commits and starts a new question attempt.
  The city and every player entity keep their current location.
- HTTP/JSON/URL/answer/manifest errors do not replace the session. Closing,
  refreshing or superseding a request aborts it and invalidates its generation;
  a late response cannot activate a unit, even if a transport ignores abort.
  Failed manifest refresh clears the old publication choices but keeps the active
  assignment and its progress, including if the assignment is no longer listed.
- The session owns an immutable normalized unit and a monotonic set of passes.
  Wrong answers and wrong reviews allow retry without revoking passes. Travel and
  cameras do not write educational state. Nothing is stored in localStorage.
- Four-question units hide the existing Q05 scene node and exclude it from X and
  completion. Five-question units restore it at the same coordinates. Existing
  marker objects/textures are reused; active labels show the unit ID instead of
  DEMO. Confirmed replacement resets colors for the new attempt only.

## Verification

Before changes, the merged baseline passed **137/137 Node tests**, with zero
failures/skips/cancellations, in **37.834 s** on Node **24.19.0**.

The focused Node run passed **71/71**, including 34 new assignment cases and the
existing education/navigation/boot/teleport tests. The Python suite passed
**5/5 tests**: the complete reference corpus covers **364 validation cases** and
**76 answer selections**, checking exact JavaScript/Python errors, normalization,
URL patterns, membership and JSON Schema acceptance. No cases were skipped.

The final full Node run passed **171/171** (137 existing + 34 new assignment
tests), with **0 failures, skips or cancellations**, in **40.691 s**. Syntax checks
passed for all **65 JavaScript** and **9 Python** files. `git diff --check` passed.
Both versions of the loopback fixture server passed nested HTML/module loading,
manifest/unit requests and unpublished-unit 404 checks, without changing the
empty public manifest.

All **15 reused files** match the pinned reference commit byte-for-byte, and its
checkout is unchanged. The Phase 1.1 configuration/coordinates/radii, navigation
module, original demo fixtures, city controllers/cameras/maps/traffic/post-
processing/geodata and Three.js import map remain byte-identical to merged main.
The original city stylesheet is unchanged. Across the 68 originally imported
files, 64 are byte-identical; only `.gitignore`, the authorized main/HTML
educational wiring and the preload inventory test differ.

The full-city browser run **passed all 12 check groups** on Linux Chromium
**154.0.8037.57**, hosted beneath **`/course/city/`**. It first exercised the full
Phase 1/1.1 demo, normal walking to all five sites, original navigation/teleports
and dialog/retry/input behavior. It then verified the actual empty public
manifest, confirmation/cancellation without city movement, v2 four-question
single-choice interaction, Q05 denial, completion and travel/color preservation,
HTTP/JSON/answer/URL failures, cancellation of an in-flight request, invalid
allowlists and a v1 five-question replacement restoring Q05. Node tests cover
both counts in both versions and stale transport completions that ignore abort.

The result log contains **no page-script errors or GPU device loss**. The
deliberately blocked font and HTTP 503 failure case produced expected resource
console errors. Startup, selection/confirmation, validated-question and completion
screenshots were inspected. Artifacts are local to
`/tmp/city-phase2-evidence/`: `results.json`, `assignment-requests.json`,
`start.png`, `question.png`, `Q01.png`–`Q05.png`, `assignment-selector.png`,
`assignment-question.png` and `assignment-four-complete.png`.

At implementation time, physical Windows Phase 2 validation was pending; the
subsequent 9/9 instructor report is recorded above. Real touch/gamepad hardware,
hardware GPU performance and other platforms were not verified by this run.

Commands from repository root:

```sh
node --test --test-reporter=tap tests/*.test.cjs tests/*.test.mjs
python3 -m unittest tests.test_assignment_contract -v
python3 tests/browser_education.py --assignments --base-path course/city/ --output /tmp/city-phase2-evidence
python3 tools/validate_assignments.py assignments/manifest.json tests/fixtures/manifest.json tests/fixtures/v2/manifest.json
```

Node's original geodata/mocked Overpass tests and the Python parity subprocess
need subprocess access. Python parity/schema tests use `jsonschema`; it is a test
dependency only. Playwright and Chromium are optional browser-test dependencies.
There is no runtime package install or build step for the city.

The browser harness uses the full original scene, native controls and unchanged
render pipeline with test-only observations/deterministic production frames.
Software Vulkan, verified transport of exact CDN bytes and existing font
fallbacks are cloud test accommodations. Intermediate GPU draws during walking
are skipped while real movement, collision, traffic and UI updates still run.
Synthetic assignment responses are routed only by the test; public files stay
empty. Screenshots/results/cache stay outside Git. No FPS or hardware-performance
claim follows from this instrumented run.

## Exact changed files

The Phase 2 diff contains **41 files**. Fifteen are unchanged reference copies;
the production additions are four small adapter/loader/session/selector modules.

| File | Reason |
| --- | --- |
| `.gitignore` | Excludes Python cache and private teacher/export directories. |
| `AGENTS.md` | Records merged prerequisite, Phase 2 authorization, preservation and review constraints. |
| `Plan.md` | Approved Phase 2 milestones and instructor-reported Windows evidence. |
| `docs/assignment-compatibility.md` | Updates port status and the location-preserving replacement policy. |
| `docs/assignment-reuse.md` | Pinned sources, permission basis, unchanged copies and adapted-code notices. |
| `docs/phase-1-results.md` | Records PR #2 merge and instructor-reported 7/7 Windows acceptance separately from cloud tests. |
| `docs/phase-2-results.md` | Implementation, exact file inventory, test evidence, limits and manual review. |
| `docs/upstream.md` | Links the approved reference reuse/notice record. |
| `assignments/manifest.json` | Empty version-1 public allowlist; no published units. |
| `schemas/assignment-v1.schema.json` | Unchanged reference v1 contract. |
| `schemas/assignment-v2.schema.json` | Unchanged reference v2 contract. |
| `schemas/manifest-v1.schema.json` | Unchanged reference allowlist contract. |
| `js/assignment-rules.js` | Unchanged reference URL patterns. |
| `js/assignment-validator.js` | Unchanged reference validation, normalization and answer acceptance. |
| `js/assignment-contract.js` | Small native ES-module compatibility bridge and original-style error summary. |
| `js/assignment-loader.js` | Relative allowlist loading, abort/generation guards and validation-before-commit. |
| `js/assignment-session.js` | Independent immutable unit data and memory-only progress; defaults to the unchanged demo. |
| `js/assignment-ui.js` | Minimal published-unit selector, explicit confirmation, status and cancellation. |
| `js/education-ui.js` | Uses active session questions/counts and shares existing modal input/pause/focus handling. |
| `js/education-terminals.js` | Reuses fixed markers/textures; updates unit labels/colors and Q05 visibility. |
| `js/main.js` | Composes loader/session/selector; filters inactive questions and guards navigation during either modal. |
| `index.html` | Six exact module preloads, a small Assignments button and native selector dialog. |
| `css/education.css` | Scoped selector styling using the existing question-dialog presentation. |
| `tools/assignment_data.py` | Unchanged reference Python contract for independent parity checks. |
| `tools/validate_assignments.py` | Unchanged read-only reference validation CLI. |
| `tests/__init__.py` | Makes local reference corpus imports unambiguous. |
| `tests/assignment.test.mjs` | 34 validation/session/allowlist/loading/failure/cancellation/staleness regressions. |
| `tests/assignment_parity.mjs` | Runs the native adapter on the shared Python corpus and answer selections. |
| `tests/test_assignment_contract.py` | Five acceptance, exact parity, schema, membership and CLI checks. |
| `tests/contract_cases.py` | Unchanged synthetic reference validation corpus. |
| `tests/contract_cases_v2.py` | Unchanged v2/answer-selection corpus. |
| `tests/fixtures/S01.json` | Unchanged synthetic four-question v1 test unit. |
| `tests/fixtures/S02.json` | Unchanged synthetic five-question v1 test unit. |
| `tests/fixtures/manifest.json` | Unchanged test-only v1 manifest. |
| `tests/fixtures/v2/S01.json` | Unchanged synthetic four-question v2 test unit. |
| `tests/fixtures/v2/S02.json` | Unchanged synthetic five-question v2 test unit. |
| `tests/fixtures/v2/manifest.json` | Unchanged test-only v2-unit manifest, still manifest version 1. |
| `tests/boot.test.cjs` | Exact preload inventory changes 34→40; canonical URL/order checks remain. |
| `tests/browser_education.py` | Retains the Phase 1/1.1 check and adds nested hosting/optional assignment checks. |
| `tests/browser_assignments.py` | Real-city Phase 2 selector/data/answer/error/travel checks with test-only HTTP responses. |
| `tests/serve_assignment_fixtures.py` | Loopback-only manual fixture server; never changes or publishes public files. |

## Windows 11 Chrome/Edge manual review

1. In the feature checkout, run `py -3 -m http.server 8000`. Open
   `http://127.0.0.1:8000/` with the original external CDN access. Use Chrome and
   Edge separately and record their actual versions; do not infer them here.
2. Verify fixed taxi startup, original city/map/traffic and Phase 1.1 navigation.
   Click Assignments: the real empty manifest must report no published units.
   Close/Escape resumes Demo Mode at the same location with the same passes.
   Complete/retry demo questions as before; Return/modes/teleports preserve passes.
3. Stop that server. For synthetic local testing only, run
   `py -3 tests/serve_assignment_fixtures.py --version 2 --prefix course/city`.
   Open `http://127.0.0.1:8000/course/city/`. This loopback test server routes test
   fixture bytes without modifying public files; never use it for deployment.
4. In Assignments select S01, click Load Unit, then Cancel. Check location and
   passes are kept. Repeat and Confirm Replacement; S01 should show 0/4 progress.
   Q05 is hidden and cannot open with X. Check the same five stored coordinates.
5. Answer S01 Q01 with a wrong label then A. It has three options. Q02 has four
   options: choose just C (or B) to pass. Reviewing with A must retain its pass.
   Q03 accepts A/B/C; Q04 accepts A. All four complete without a fifth question,
   exit, timer, video or Form interface.
6. Return to Start; switch ground modes near Central Park, try the independent
   helicopter, camera changes and full-map/preset teleport. Verify the assignment,
   passes and green screens remain. During either modal try movement, mode/map/
   camera keys, X and Return: simulation must pause and shortcuts stay blocked.
   Check Tab, Escape, mouse controls and held-key cleanup after closing.
7. Select S02 (five questions), confirm and verify 0/5, restored Q05 and unchanged
   city location. In v2 its accepted labels are Q01 A; Q02 B/C; Q03 A/B/C; Q04 A;
   Q05 B/C. Each student answer still uses one radio selection.
8. Stop the fixture server and repeat with `--version 1` to exercise legacy four-
   and five-question units, four choices each, and accepted labels A/B/C/D/(A).
   These synthetic files must remain in test paths and out of publication.
9. Use browser DevTools request blocking/offline mode during unit loading; cancel
   before a slow response, retry after a failure, and check the old attempt and
   positions survive. Automated tests also cover malformed JSON, invalid URLs/
   answers, strict allowlisting and late/out-of-order responses.
10. Stop the test server and confirm `git status --short` is clean. The real
    `assignments/manifest.json` must still be empty. Record physical results and
    repeat relevant original city regression checks before approving this draft.

That Phase 2 review is complete as recorded above. Phase 3 has separate approval;
this historical report does not authorize merging or deploying later work.
