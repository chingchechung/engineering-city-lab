# Phase 1 and 1.1 — synthetic question MVP and navigation

Prepared 2026-10-24 (Asia/Taipei) on `feature/phase-1-education-mvp`, from reviewed
main `974fddf2feecc96faf6856818f2eb452f83991df` (merged Phase 0 PR #1). The instructor
explicitly extended Phase 1 from placeholders to an end-to-end synthetic demo.
This change stops at a draft PR for review; it does not authorize Phase 2 or merging.

Phase 1/1.1 was subsequently reviewed and PR #2 merged as
`43f4b2660d11e56c091df89888df7b02e9726a70` on 2026-10-24 (Asia/Taipei).
The instructor reports **7/7 Windows 11 manual acceptance checks passed**.
This is instructor-reported evidence; browser versions, GPU measurements and
FPS were not provided. The historical cloud results below remain separate.

The instructor subsequently approved Phase 1.1 on this same draft PR branch,
starting at `f9e9d86`: distribute terminals, synchronize explicit ground-mode
changes and add Return to Start. This supersedes the original same-block layout
and independent ground-mode switching; the helicopter exception stays intact.

## Implemented behavior

- Every startup chooses the original taxi at `(3.6, 0, 410.6)`, heading 0. The
  old `nyc-player-state` restore is deliberately ignored for every mode. Other
  entities retain their original constructor starts. Subsequent explicit ground-mode
  changes use the nearby placement behavior described below.
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
- Helicopter answering is disabled at every altitude. Explicit ground-to-ground
  switches capture the source position/heading and safely place the selected
  entity within 20 m. Walking arrivals prefer sidewalks/open park areas; vehicles
  prefer roadway space with body-width clearance. The original safe-placement
  search handles buildings/player entities; additional arrival checks reject
  overlap with current cars, buses, highway vehicles and pedestrians. No physics,
  collision geometry or traffic behavior is changed.
- Ground-to-helicopter and helicopter-to-ground changes preserve the selected
  entity's own in-memory location. No ground vehicle is copied to an airborne
  position. There is no continuous synchronization; repeated selection of the
  current mode does not relocate it.
- Return to Start keeps the current ground mode, or selects car from helicopter,
  and safely returns within 20 m of the configured original anchor. It uses the
  same teleport/input/camera reset path and updates the map waypoint. Passes and
  green completion screens remain. No scene reconstruction or page reload occurs.
- Both navigation actions preflight before moving. A distant fallback from the
  original 256 m placement search is rejected. If no suitable nearby slot is
  found, the current mode and all entity positions stay unchanged and an explicit
  status explains the failure. Return is disabled and guarded during questions.
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
| Q01 | -55 | 391 | North sidewalk of W 37th Street, west of Fifth Avenue; easy approach along the cross street. |
| Q02 | 11 | 422.6 | Fifth Avenue east sidewalk; remains convenient from the starting taxi. |
| Q03 | 60 | 391 | North sidewalk of E 37th Street; adds an east-side cross-street approach. |
| Q04 | -60 | 484.5 | South sidewalk of W 36th Street; a separate nearby block/corner route. |
| Q05 | 65 | 328.2 | South sidewalk of E 38th Street; extends the short loop north of the start. |

The configuration is the sole source of these positions. The sites sit outside
GEO building-lot rectangles and are spread over Fifth Avenue and three cross
streets. Simple sidewalk routes from the start are approximately 14–155 m;
actual distances measured by normal movement are recorded below. Routes follow
Fifth Avenue's sidewalk to the relevant cross street, then proceed along its
sidewalk; they do not cut across building interiors. Ordinary city pedestrians
and traffic retain their original routes. The markers remain nonblocking.

The Phase 1 survey previously moved Q02 one metre streetward to clear facade
occlusion. Phase 1.1 retains that position and surveys the four new cross-street
sites. Full-city software-rendered screenshots and ordinary walking controls
provide cloud evidence; physical Windows hardware review remains separate.

## Exact changed files

| File | Why |
| --- | --- |
| `AGENTS.md` | Records merged Phase 0 and the instructor's Phase 1/1.1 authorization and review gate. |
| `Plan.md` | Updates the approved milestones, fixed-site decision and results link. |
| `js/education-config.js` | Fixed start/sites, configurable interaction limits and pure proximity/obstruction checks. |
| `js/education-session.js` | Five synthetic fixtures and a small in-memory, monotonic completion set. |
| `js/education-navigation.js` | Bounded, surface-aware ground switching, traffic occupancy and Return to Start through the existing teleport callback. |
| `js/education-terminals.js` | Independent five-marker scene group and pass-color updates. |
| `js/education-ui.js` | Safe text rendering, native answer dialog, progress, X/focus guards and input cleanup. |
| `js/main.js` | Five imports, educational composition, explicit navigation actions and the existing simulation pause gate. |
| `index.html` | Five educational module preloads, scoped demo/dialog markup and a compact Return to Start toolbar button. |
| `css/education.css` | Scoped responsive demo styling; respects the existing H clean-view toggle. |
| `tests/boot.test.cjs` | Exact preload count changes from 29 to 34; existing canonical URL/order assertions retained. |
| `tests/education.test.mjs` | Fourteen focused configuration/proximity/height/obstruction/speed/startup/session/frame-gate regressions. |
| `tests/education-navigation.test.mjs` | Eighteen real-controller placement/navigation regressions, including Central Park, traffic, distant-fallback rejection, helicopter exceptions and dialog guards. |
| `tests/browser_education.py` | Optional full-city real Chromium/Playwright check with screenshots and local diagnostics. |
| `docs/phase-1-results.md` | This implementation, verification and Windows review record. |

Of the original 68 imported files, **65 remain byte-identical**. Only main, HTML
and the boot inventory test changed. Original city geometry, data, controller
physics, cameras, map/GPS/teleport implementation, traffic, audio, lighting,
shaders, post-processing, tools, notices and original CSS are unchanged. The
import-map block remains byte-identical, including every moving `@dev` URL.

The Phase 1.1 increment from `f9e9d86` changes exactly twelve files: `AGENTS.md`,
`Plan.md`, this record, `css/education.css`, `index.html`, `js/main.js`,
`js/education-config.js`, the new `js/education-navigation.js`,
`tests/boot.test.cjs`, `tests/education.test.mjs`, the new
`tests/education-navigation.test.mjs` and `tests/browser_education.py`.
The question fixtures/answer logic, dialog module and marker construction are
unchanged from Phase 1.

## Verification

For Phase 1.1, first rerunning the unchanged **119-test** baseline passed with
**0 failures, skips or cancellations** in **46.093 s**. After the changes, the full
suite passed **137/137** (105 imported, 14 original education and 18 new navigation
cases), with **0 failures, skips or cancellations**, in **59.212 s** on Node
**24.19.0**. Syntax checks for all **57 JavaScript files**, Python compilation,
local documentation links and `git diff --check` also passed.

The updated full-city browser check **passed** on Linux Chromium
**154.0.8037.57**, using software Vulkan. It reached and answered every terminal
through the unchanged walking/turning/collision code, with these measured routes:

| Terminal | Walking distance from returned walking arrival |
| --- | ---: |
| Q01 | 84.49 m |
| Q02 | 11.46 m |
| Q03 | 67.77 m |
| Q04 | 144.02 m |
| Q05 | 138.44 m |

Each route starts after Return to Start in person mode, within 20 m of the fixed
taxi anchor, and follows the Fifth Avenue sidewalk and the relevant cross street.
These are actual traversed paths, not shortest-path guarantees. All are below
the requested approximately 250 m. The start, dialog and five final-site images
were inspected: every sign is readable without a facade hiding it.

Central Park ground switches remained within 20 m. Helicopter transitions kept
independent locations. Return from all four modes preserved five passes and
marker colors, stopped motion and updated the waypoint. Native X, retry, focus,
dialog blocking/pause, held-key cleanup, map/preset teleport and moving-car checks
also passed. The result log reported **no page-script errors or GPU device loss**;
an intentionally blocked external font request produced one resource-error
console message. Artifacts: `/tmp/city-phase11-evidence/results.json`,
`start.png`, `question.png`, and `Q01.png`–`Q05.png` in that directory (local review
artifacts, outside Git).

Historical Phase 1 results, before the Phase 1.1 increment:

For the original Phase 1 implementation, the imported suite passed **105/105** on Node 24.19.0 in 36.186 s.
The Phase 1 combined suite passed **119/119** (the original 105 plus 14 education
cases), with **0 failures, skips or cancellations**, in **75.204 s**. Syntax
checks passed for all **55 JavaScript files** and the Python browser check;
`git diff --check` and local Markdown link checks passed.

The Phase 1 full-city browser run **passed** on Linux Chromium **154.0.8037.57**,
with no page-script errors or GPU device loss on the successful Vulkan run.
All native interaction checks below passed against the revised Q02 coordinate,
including bicycle answering, moving-car rejection and map/preset teleportation.
Startup, dialog and all five final-site screenshots were inspected. At that
stage, physical Windows 11 Chrome/Edge verification was pending; the subsequent
instructor-reported acceptance is recorded above.

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
stepping to bound software GPU work; route traversal skips intermediate GPU draws
while still running the production movement, collision, traffic and UI updates.
No debug API or test frame scheduler is shipped in the application. Frames run
the unchanged production callback.

The updated browser check covers fixed startup, the actual nearest eligible
startup question (without assuming its ID), X/repeat/modifier/typing guards,
incorrect/correct/reopened answers, focus, shortcut suppression, dialog pause,
held-key cleanup and helicopter denial. Each site is reached through the original
movement/turning/collision code along a normal walking route from Return to Start,
not by teleporting directly to the question. It also exercises completion,
map/preset travel, nearby Central Park mode changes, helicopter independence,
Return from every mode, waypoint updates and retained completion colors. It
captures start/question/per-terminal images and a JSON result log.
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
   in DevTools, then reload. It must still start in the taxi at the fixed site,
   and the audio preference survives. Subsequent explicit ground-mode changes
   should use nearby placement, as checked below.
2. Read the nearest-terminal prompt and press X. For the current layout the
   convenient Fifth Avenue site is Q02; the selection always follows actual
   proximity/eligibility. Choose a wrong answer, retry correctly, close and
   reopen. A later wrong answer must not revoke the pass. Synthetic accepted
   labels are **A, B, C, A, B** for Q01–Q05.
3. While answering, try W, mode digits, V, M, B, pointer/touch and Return to Start.
   Position/time should stay paused, Return should be disabled, and the scene
   continues rendering. Tab stays in the dialog; Escape/Close restores control.
   Held X/movement must require release before activating again.
4. Use ordinary movement to visit the new 37th Street west/east sites, the 36th
   Street west site and the 38th Street east site. Use sidewalks and cross-street
   corners rather than cutting through building lots. Inspect label readability
   from walking and driving approaches. Car/bicycle need speed <= 0.5 m/s;
   radii remain 3/18/8 m for walking/car/bicycle.
5. Use a preset teleport near Central Park, then switch car → person → bicycle
   → car. Each selected ground entity should appear safely within about 20 m,
   rather than returning to the original spawn. Test near buildings/curbs and
   traffic. If no suitable slot is found, check clear failure feedback and no
   distant relocation. Re-selecting the current mode should not relocate it.
6. Select helicopter, explore/fly using the original controls, then select a
   ground mode: it should use that ground entity's own in-memory location, never
   copy the airborne helicopter position. X remains disabled for helicopter.
7. From a far-away preset, click Return to Start in each mode. Ground modes stay
   selected; helicopter chooses car. Check safe arrival near the original anchor,
   stopped motion, fresh chase view, waypoint and unchanged passes/green screens.
   Return is navigation, not a restart. If all nearby slots are blocked, it must
   retain the original mode/location and explain the failure.
8. Complete all five and confirm the message without an exit. Repeat map search,
   pan/zoom/GPS, arbitrary-map and preset teleports, camera/time changes, H clean
   view, audio, focus/tab interruptions and available touch/gamepad hardware.
   Progress stays in memory until a deliberate page reload.

Physical Windows 11 checks were not performed by cloud automation; the instructor
subsequently reported the 7/7 acceptance result above. Intel GPU measurements,
macOS/Safari, mobile and real gamepad hardware were not independently verified.
Phase 2 is now separately authorized following the verified PR #2 merge.
