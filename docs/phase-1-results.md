# Phase 1 — minimal synthetic question MVP

Prepared 2026-10-24 (Asia/Taipei) on `feature/phase-1-education-mvp`, from reviewed
main `974fddf2feecc96faf6856818f2eb452f83991df` (merged Phase 0 PR #1). The instructor
explicitly extended Phase 1 from placeholders to an end-to-end synthetic demo.
This change stops at a draft PR for review; it does not authorize Phase 2 or merging.

## Implemented behavior

- Every startup chooses the original taxi at `(3.6, 0, 410.6)`, heading 0. The
  old `nyc-player-state` restore is deliberately ignored for every mode. Other
  entities retain their original constructor starts and independent locations.
  Existing travel-state saves and the unrelated audio preference remain; demo
  answers/progress are never written to storage.
- Five nonblocking gold terminals carry Q01–Q05/DEMO signs. A passed terminal's
  screen turns green. The signs use five small generated canvas textures,
  existing Three.js geometry and node-material classes; no external assets,
  new lights, colliders or city regeneration are introduced.
- X selects the nearest eligible terminal from the active entity's horizontal
  world position. Walking uses 3 m, car 18 m, bicycle 8 m. Car/bicycle need actual
  horizontal speed <= 0.5 m/s, including car impulse velocity. Height/surface
  checks reject elevated approaches; segment tests against the city's nearby
  static AABB/OBB collision bounds prevent answering through buildings.
- Helicopter answering is disabled at every altitude. Mode changes retain the
  original independent-location behavior; they never transport another vehicle.
- A native accessible dialog shows a synthetic question, one-choice options,
  submit, feedback and close. Incorrect answers permit immediate retry without
  removing any completion. Correct answers pass only that ID. Reopening and
  reviewing a completed question cannot revoke it. All five passes show a demo
  completion message, with no exit/travel requirement.
- Progress exists only in this page's memory and resets on reload. It survives
  ordinary mode/camera changes, map use and both teleport paths.
- While answering, capture-phase key handling blocks city shortcuts and native
  modal behavior blocks background pointer interaction. Touch/gamepad input and
  any in-progress orbit capture are cleared. Controller, camera, street/highway
  physics and signal time pause together, while the existing renderer continues.
  Close/Escape restores controls; held keys stay suppressed until release.
  Frame wall time still advances while paused, preventing resume catch-up.

No real unit loader, v1/v2 schema port, teacher GUI changes, course questions,
videos, Forms, login, analytics, map budgets, maze or exit system was added.
`ece_hw_webproject` is untouched. The demo is explicitly labeled as synthetic
interaction data, not Digital Electronics coursework.

## Final fixed sites and rendered survey

All bases use y = 0.22. The registry is immutable and shared by all travel modes.

| ID | x | z | Survey decision |
| --- | ---: | ---: | --- |
| Q01 | -12 | 422.6 | Original proposed west-sidewalk site retained. |
| Q02 | 11 | 422.6 | Moved 1 m toward the street from proposed x = 12; the close approach view partly hid its label behind a facade. |
| Q03 | -12 | 442.6 | Original proposed west-sidewalk site retained. |
| Q04 | 12 | 442.6 | Original proposed east-sidewalk site retained. |
| Q05 | -12 | 462.6 | Original proposed west-sidewalk site retained. |

The full original city rendered in Linux Chromium with software Vulkan. The
initial taxi view and close walking views were inspected, and the real controller's
existing safe teleport method reached all five sites. Q02 was adjusted after
that survey. The final browser run verifies the revised position. This is
rendered-scene evidence, not physical Windows hardware/performance certification.
Ordinary city pedestrians continue to use their original sidewalks; the markers
do not block or redirect them. Some original awnings cover the nearby sidewalk
camera view; the other four question labels remain readable in the surveyed views.

## Exact changed files

| File | Why |
| --- | --- |
| `AGENTS.md` | Records merged Phase 0 and the instructor's expanded Phase 1 authorization/review gate. |
| `Plan.md` | Updates the approved milestones, fixed-site decision and results link. |
| `js/education-config.js` | Fixed start/sites, configurable interaction limits and pure proximity/obstruction checks. |
| `js/education-session.js` | Five synthetic fixtures and a small in-memory, monotonic completion set. |
| `js/education-terminals.js` | Independent five-marker scene group and pass-color updates. |
| `js/education-ui.js` | Safe text rendering, native answer dialog, progress, X/focus guards and input cleanup. |
| `js/main.js` | Four imports, fixed-start call, marker/UI composition and a narrow simulation pause gate. |
| `index.html` | Four canonical module preloads, separate stylesheet and scoped demo/dialog markup. |
| `css/education.css` | Scoped responsive demo styling; respects the existing H clean-view toggle. |
| `tests/boot.test.cjs` | Exact preload count changes from 29 to 33; existing canonical URL/order assertions retained. |
| `tests/education.test.mjs` | Fourteen focused configuration/proximity/height/obstruction/speed/startup/session/frame-gate regressions. |
| `tests/browser_education.py` | Optional full-city real Chromium/Playwright check with screenshots and local diagnostics. |
| `docs/phase-1-results.md` | This implementation, verification and Windows review record. |

Of the original 68 imported files, **65 remain byte-identical**. Only main, HTML
and the boot inventory test changed. Original city geometry, data, controller
physics, cameras, map/GPS/teleport implementation, traffic, audio, lighting,
shaders, post-processing, tools, notices and original CSS are unchanged. The
import-map block remains byte-identical, including every moving `@dev` URL.

## Verification

Before edits, the imported suite passed **105/105** on Node 24.19.0 in 36.186 s.
The final combined suite passed **119/119** (the original 105 plus 14 education
cases), with **0 failures, skips or cancellations**, in **75.204 s**. Syntax
checks passed for all **55 JavaScript files** and the Python browser check;
`git diff --check` and local Markdown link checks passed.

The final full-city browser run **passed** on Linux Chromium **154.0.8037.57**,
with no page-script errors or GPU device loss on the successful Vulkan run.
All native interaction checks below passed against the revised Q02 coordinate,
including bicycle answering, moving-car rejection and map/preset teleportation.
Startup, dialog and all five final-site screenshots were inspected. Physical
Windows 11 Chrome/Edge verification remains for the instructor's review.

Commands from the repository root:

```sh
node --test --test-reporter=tap tests/*.test.cjs tests/*.test.mjs
python3 tests/browser_education.py --output /tmp/city-education-evidence
```

The Node suite needs subprocess access for the original geodata/mocked Overpass
tests. The optional browser check needs Playwright for Python plus Chromium;
`BROWSER_EXECUTABLE` may select an installed Chromium binary. It uses the complete
actual city, synthetic data, native keyboard/radio/button/dialog events, stale
localStorage, real controllers/teleport/map and the actual render pipeline.
Test-only module interception exposes observations and deterministic frame
stepping to bound software GPU work; no debug API or test frame scheduler is
shipped in the application. Frames run the unchanged production callback.

The browser check covers fixed startup for all modes, X/repeat/modifier/typing
guards, nearest Q02 at startup, incorrect/correct/reopened answers, focus, city
shortcut suppression, paused position/time, held-key cleanup, helicopter denial,
visits to all five sites, completion, map/preset teleports, driving and bicycle
answering. It captures start/question/per-terminal images and a JSON result log.
Artifacts and CDN test cache stay outside Git.

In this cloud environment, Chromium does not inherit the proxy CA trust. The
test transports the exact original CDN URLs through Python urllib with normal
TLS verification and fulfills those bytes unchanged. Restricted external font
requests are omitted in this test; the existing system-font fallbacks are used.
Software Vulkan launch flags and frame stepping are testing accommodations,
not product rendering changes. Earlier default software-adapter attempts lost
the GPU device, and continuous software submissions stalled input capture;
neither attempt established a passing visual check. No FPS claim follows from
the instrumented browser's HUD or screenshot.

## Windows 11 Chrome/Edge review

From a checkout of the feature branch, open PowerShell in the repository folder:

```powershell
py -3 -m http.server 8000
```

Open `http://127.0.0.1:8000/` in Chrome, then Edge, with external CDN access.
No Node/npm install is needed to play. Stop the server with Ctrl+C when finished.

1. Verify car mode and the original taxi start. To test stale startup, use a
   test browser profile and set `nyc-player-state` to a different position/mode
   in DevTools, then reload. It must still start in the taxi at the fixed site;
   the other modes must keep their original starts, and audio preference survives.
2. At startup, the nearest eligible terminal is Q02. Press X, choose A and submit
   for incorrect feedback, then choose B for correct feedback. Check 1/5 progress.
   Close and reopen; a later wrong answer must leave Q02 completed.
3. While the dialog is open, hold W and try digits, V, M, B and pointer/touch
   movement. Position and city physics should stay still; rendering continues.
   Tab stays in the dialog, Escape/Close works, and held movement/X cannot
   activate again until released. Check normal controls afterward.
4. Drive south a short distance and stop beside each marker, steering toward the
   desired sidewalk if interaction radii overlap. Only the nearest valid marker
   opens. The prompt requires car/bicycle speed <= 0.5 m/s; brake and release
   drive controls. Walk within 3 m or cycle within 8 m to check those modes.
   The five synthetic accepted labels are **A, B, C, A, B** in Q01–Q05 order.
5. Complete all five and verify the demo completion message without an exit.
   Travel, switch cameras/modes and use full-map and preset teleports: progress
   remains. Refresh once to verify that memory-only progress starts at 0/5.
6. Select helicopter mode. Flying and E/Space/Q/C retain original behavior;
   X never opens a question, even if the helicopter is low. Returning to car
   must use the car's own independent position.
7. Repeat the Phase 0 city checklist: all modes/cameras/time presets, collision,
   traffic/pedestrians, horn/audio, minimap/full map/search/pan/zoom/GPS/teleports,
   H clean view, focus/tab interruptions and any available touch/gamepad hardware.
   Verify marker readability from car and walking approaches on both sidewalks.

Physical Windows 11 checks, Intel GPU behavior, macOS/Safari, mobile and real
gamepad hardware were not verified in cloud automation. Record those observations
during instructor review. Do not merge this PR or start S01–S12 integration
until that review explicitly authorizes the next step.
