# Phase 0 — baseline verification record

Date: 2026-10-23 (Asia/Taipei). Code under test:
`cca9c12a096951d63fee1d26904c04be0a128cef`, also the unchanged imported runtime on
the preparation branch. Environment: Linux x86_64, Node **v24.19.0**, Python
**3.12.14** for a local HTTP smoke check. No dependency install or source fix was
needed. No educational tests or implementations were added.

## Automated results

| Check actually run | Result |
| --- | --- |
| Imported Node suite, with subprocess access | **105 passed, 0 failed, 0 skipped/cancelled**; 13 test files; 57.497 seconds |
| `node --check` across runtime modules, test/helper JS and tool MJS | **50/50 files passed** |
| `bash -n tools/overpass.sh` | Passed |
| Temporary local Python HTTP server and GETs for entry, CSS and 29 preloaded modules | **31/31** returned HTTP 200 and nonempty bodies |
| Upstream import comparison | Only `README-initial.md` differs from upstream commit `4b899b0`; city/data/tests match |

The initial sandboxed suite reported two failing **files**, geodata and Overpass.
Running with test isolation disabled exposed **97 passing cases and 8 blocked
cases**: the one geodata subprocess and seven mocked Overpass subprocess cases
returned `spawnSync ... EPERM` for Node/bash. Direct Overpass execution confirmed
the same restriction. The unchanged full suite was then rerun with subprocess
permissions and passed all 105 cases. No failures were suppressed or assertions
changed. Overpass tests use a local fake curl; this does not validate live APIs.

Reproduce the successful suite from the repository root:

```sh
node --test --test-reporter=tap tests/*.test.cjs tests/*.test.mjs
```

Allow child processes, temporary files and Bash. The geographic test runs the
builder with an 8 GiB V8 heap ceiling in a temporary checkout with spaces and
non-ASCII characters; leave enough memory/time. It uses the checked-in data and
does not overwrite the repository's generated geography. There is no npm test,
lint or build script and no imported CI workflow to run.

Syntax commands used:

```sh
for file in js/*.js tests/*.cjs tests/*.mjs tests/helpers/*.cjs tools/*.mjs; do
  node --check "$file" || exit
done
bash -n tools/overpass.sh
```

The HTTP smoke used Python's `ThreadingHTTPServer` on a temporary loopback port
and `urllib.request` to fetch `/index.html`, `/css/style.css` and every local
modulepreload URL parsed from the HTML. The server was shut down afterward.
This checks static serving, not module execution, CDN availability or rendering.

## Existing coverage

| Imported test file | Cases | What it establishes |
| --- | ---: | --- |
| `boot.test.cjs` | 2 | Import-map/preload/style ordering, shared Three alias, exact 29 canonical native module preloads and relative URL consistency. |
| `cameras.test.cjs` | 13 | Mouse/touch gestures, capture cleanup, pinch bounds, teleport chase/orbit reset. |
| `controllers.test.cjs` | 24 | Input blending/release/interruption, analog scaling for all four modes, teleport reset, overlapping/oriented collision clearance, shoreline/altitude and other-player clearance. |
| `facade-projection.test.cjs` | 6 | Numeric TSL facade coordinate/orientation stability across rotations and scales. |
| `geodata.test.mjs` | 1 | Local builder runs with default paths in a spaced/non-ASCII temporary checkout; resulting blocks/road graph are nonempty. |
| `nyc-map.test.cjs` | 12 | Canvas/world conversion across DPR/layout sizes, pointer ownership, click teleport, pan/cancel/close cleanup and zoom/hover. |
| `overpass.test.mjs` | 7 | Fake-download validation, preserving prior data after errors, cleanup, retry and atomic replacement. |
| `smoke-texture.test.cjs` | 1 | Cached smoke generation preserves texture bytes and reduces hash calls. |
| `teleports.test.cjs` | 3 | All eight preset buttons match roadway destinations; One WTC arrival; shared map/preset resets and resolved waypoint. |
| `touch-controls.test.cjs` | 11 | Analog deadzone/clamp, simultaneous pointer ownership, modes/availability, disabled controls and interruption cleanup. |
| `traffic-performance.test.cjs` | 7 | Pedestrian gait/pose visibility behavior and bounded live/idle spark uploads. |
| `traffic.test.cjs` | 13 | Elevation-aware street/highway player checks, police signal/yield behavior, cars/pedestrian replenishment and sidewalk fallback. |
| `vehicle-lights.test.cjs` | 5 | Shared headlamp profile, modeled lamp/target placement, yaw/slope handling. |
| **Total** | **105** | Imported regressions; no education integration yet. |

Most suites evaluate production functions or source sections using explicit
Three/DOM/canvas stubs through `tests/helpers/module.cjs` or VM harnesses. Numeric
shader checks are not GPU shader compilation. No full browser automation, image
comparison, audio suite or gamepad-specific test file is present. The geodata
test checks build success/nonempty output, not byte-for-byte generator parity.

`tools/benchmark-pedestrians.mjs` is an optional benchmark, not a default test.
It requires an existing real `three.core.js` path (or `THREE_CORE_PATH`), verifies
hidden/visible rig parity and measures CPU animation for 340 rigs. It was **not
run**: no matching local dev-branch Three.js core is bundled, and installing or
substituting a dependency would not establish the original browser baseline.
It would not measure GPU rendering or whole-city FPS in any case.

## Physical browser evidence and remaining checks

The instructor reports that the imported original city already ran successfully
on **Windows 11 with Chrome and Edge**. Treat this as instructor-provided baseline
evidence. Exact browser builds, GPU, per-feature checklist and measured FPS were
not supplied. Phase 0 did not rerun a physical Windows session or the WebGPU
renderer; no macOS/Safari, mobile or performance claim follows from these tests.

For later comparison, serve the repository from HTTP(S), for example:

```sh
python3 -m http.server 8000
```

Use a browser with external dependency access. Before Phase 1 changes, record
the baseline and then repeat the same checks on its feature branch:

- Fresh browser state starts in the taxi at `(3.6, 0, 410.6)`, heading 0; separately
  verify the original saved-position/active-mode return behavior. In a test-only
  profile, remove only `nyc-player-state` when checking first-visit behavior.
- Loading overlay completes; inspect console/network and note `[init]` timing
  and actual `THREE.REVISION`. Record browser/GPU versions and CDN snapshot when
  available; a moving `@dev` import can change between sessions.
- Walk/jump/sprint, drive/reverse/boost/steer, cycle and fly/ascend/descend. Check
  collisions, traffic, police, pedestrians, vehicle lights and horn/audio mute.
- Exercise all eleven cameras, mouse orbit/wheel, time presets, HUD hide/show,
  viewport resizing and touch/gamepad paths where hardware is available.
- Open the full map using M and the toolbar/radar; search, pan, zoom, center and
  fit-all. Check traffic/player/waypoint display and no imposed time budget.
- Exercise all eight preset teleports and arbitrary full-map click teleports in
  different modes, including blocked destinations; verify stopped arrival,
  camera/gesture reset and resolved waypoint. Preserve the full city extent.
- Change focus, hide/restore the tab and release held inputs; check no stuck
  movement. Inspect subdirectory hosting as well as the server root.

After Phase 0 documentation, compare the branch against the baseline to confirm
only the six new Markdown files are present. Review Phase 0 before any feature
work; terminal visibility, question dialogs and JSON integration are not tested
or claimed at this milestone.
