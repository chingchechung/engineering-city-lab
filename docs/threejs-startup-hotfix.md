# Three.js WebGPU startup hotfix

Prepared 2026-11-06 (Asia/Taipei) for instructor review on
`fix/pin-threejs-r187`. This request separately authorizes dependency pinning;
the Phase 4 dependency freeze in older documents is historical.

## Baseline and diagnosis

Before editing, GitHub fetch/API checks confirmed `main` and the `v1.0.0` tag
both resolve to `38b1dfdd73d766ec1d01999216b24dfca2126fad`, there were no open
PRs, and the current release was published, neither draft nor prerelease.
Read `AGENTS.md`, `Plan.md`, `docs/upstream.md`, `docs/architecture.md` and
`docs/phase-4-results.md`. The tag/release remain unchanged.

Confirmed evidence:

- Chromium 154.0.8037.57 reproduced the original unmodified page's error:
  `The requested module './three.tsl.js' does not provide an export named 'StorageStructNode'`.
  The original loading text remained visible and the viewport contained zero
  canvases. This is an ES-module graph linking failure, before `main.js` can
  evaluate or call `initApp()`; a catch inside `initApp()` cannot handle it.
- The old import map used four floating `mrdoob/three.js@dev` URLs. Separate
  verified-TLS fetches of the same URLs returned different bytes during this
  investigation. The graph fetched for the failed browser run was incompatible.
  Its WebGPU build references `StorageStructNode`, while its TSL build contains
  no such symbol. The fixed r187 builds consistently do not require that symbol;
  no export shim or renderer modification is needed.
- Current upstream Slop New York's `main/index.html` uses the proposed npm
  `three@0.187.0` URLs for all four entries. Its HTML was read only; no later
  upstream city code was copied. The npm package metadata identifies `0.187.0`.
- The fixed WebGPU, TSL, core, ClusteredLighting and SSRNode resources returned
  HTTP 200 and the expected JavaScript MIME type. Browser execution, rather than
  mere HTTP success or a version comment, determines compatibility below.

The exact CDN cache/edge history and upstream change responsible for the original
mix are **not independently established**. The evidence supports an incompatible
floating module graph, not a claim that a particular cache or upstream commit
caused the incident. No immutable Three.js SHA was recorded for the instructor's
earlier successful v1.0.0 run, so that last working SHA cannot be inferred.

Failed browser-run build responses (all under
`https://cdn.jsdelivr.net/gh/mrdoob/three.js@dev/build/`):

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `three.webgpu.js` | 1,345,062 | `6759286fc12010990196430d9e4cad68f56d67471e0d5f6a037824d17eddff78` |
| `three.tsl.js` | 1,065,544 | `d8f3cdb8b85b799a5631bd9a8d77e185d88ce1eb1bb051f48b332728a5423e3f` |
| `three.core.js` | 1,476,687 | `619f78b100291b82819c0fac5bc07282d0f4f263afcf8c80b05692c84625d49a` |

Fixed responses used by the successful startup test (relative to
`https://cdn.jsdelivr.net/npm/three@0.187.0/`):

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| `build/three.webgpu.js` | 1,350,894 | `eafead3154ec06093f3108bddceab360f048a6fcebd7c085d5aae0ab5404bd25` |
| `build/three.tsl.js` | 1,065,544 | `d8f3cdb8b85b799a5631bd9a8d77e185d88ce1eb1bb051f48b332728a5423e3f` |
| `build/three.core.js` | 1,474,799 | `613e370f76638fdef83926642bf256dc9615684922de1ce1f63a8583e5d78578` |
| `examples/jsm/lighting/ClusteredLighting.js` | 4,240 | `28d00d4a745a8927d7e0f0d8664d94d23d98ffea120ff54183b40973be45bf17` |
| `examples/jsm/tsl/display/SSRNode.js` | 46,020 | `3f59131d1682a9f0738e7e84060d526286c43566df141239d11401e87a8d2480` |

## Implementation and exact changed files

| File | Change |
| --- | --- |
| `index.html` | Fix all four aliases/addon prefix to npm `three@0.187.0`, preserving one canonical WebGPU module instance. Add an isolated inline startup error observer before the entry; the existing native entry and 40 preloads stay intact. |
| `tests/boot.test.cjs` | Reject floating/mixed/unreviewed Three.js versions and duplicate alias URLs; retain canonical preload checks and account for the startup observer. |
| `tests/browser_startup.py` | Native-browser module-link/download/init-rejection checks, mobile failure-message bounds and no reactivation after successful startup. |
| `tests/browser_education.py` | Preserve existing full-city workflow; additionally check the WebGPU backend, cyclist propulsion/helicopter ascent, all 11 cameras and four light presets; record exact resolved CDN URLs/bytes/hashes. Test instrumentation remains outside the distributed runtime. |
| `docs/threejs-startup-hotfix.md` | This diagnosis, results, review checklist and deployment/rollback plan. |

No production JavaScript, city geometry, shaders, simulation, physics, audio,
education logic, JSON validator/schema, assignment file, teacher GUI or unrelated
dependency changed. Only `index.html` changes in the 47-file runtime package.
The public manifest remains empty. There is no backend or offline bundle.
The final package has 2,605,152 content bytes; its other 46 files match
`v1.0.0` byte-for-byte.

The startup observer handles global script/linking errors, failed module script
loads, and unhandled initialization rejections while the existing overlay is
visible. It stops the indeterminate animation and gives a bounded, readable
dependency/WebGPU failure message. Native console errors remain available;
events are not suppressed. Font/image failures are not treated as module failures.
After startup hides the overlay, errors do not reopen it. This is not a timeout,
retry system, device-loss recovery system or broad loading redesign. A request
that never settles can still require browser/network diagnosis.

## Automated verification

Before changes: **189/189 Node**, **11/11 Python**, 364 validation cases and
76 answer selections, syntax (66 JS / 15 Python), and 47-file package integrity
passed. The initial restricted-shell attempts could not run subprocess/network
tests fully; the complete suites were rerun with the necessary execution access.

After changes: **190/190 Node**, **11/11 Python**, unchanged contract parity,
syntax (66 JS / 16 Python), empty manifest and 47-file package integrity passed.

```sh
node --test --test-reporter=tap tests/*.test.cjs tests/*.test.mjs
python3 -m unittest tests.test_assignment_contract tests.test_release -v
python3 tools/check_release.py --syntax
python3 tools/check_release.py
python3 tools/package_release.py --output /tmp/city-hotfix-review-package
python3 tests/browser_startup.py --site-root /tmp/city-hotfix-review-package --output /tmp/city-hotfix-startup-review
python3 tests/browser_learning_dom.py --output /tmp/city-hotfix-dom
python3 tests/browser_release.py --site-root /tmp/city-hotfix-review-package --output /tmp/city-hotfix-static-browser
python3 tests/browser_education.py --workflow --base-path course/city/ --site-root /tmp/city-hotfix-final-package --output /tmp/city-hotfix-final-browser
```

The output directory for packaging must not already exist. Browser scripts need
Python Playwright and Chromium. The existing CI includes the new Node dependency
check; full WebGPU/browser tests remain separately executed.

Native-DOM: three groups / three explicitly activated intercepted provider
actions, no page errors. Static package: three groups covering real nested
tilde-prefixed paths, MIME/path behavior, empty manifest and license attribution.
Startup: four expected failure/lifecycle cases, including the reproduced missing
export before entry evaluation; its intentional page errors are test evidence.

Full-city: **22/22 groups passed**, zero page-script errors and no GPU device
loss. The original 19 groups cover all five normally walked terminal routes,
Demo, v2 four-question and v1 five-question units, retry/review, explanations,
Form gates, native external actions, mobile HUD, map/teleports, Return and safe
failed/cancelled/stale replacements. Three additional groups cover cyclist
propulsion/helicopter ascent, all eleven rendered camera presets and all four
rendered lighting presets (including night clustered lights, shadows, SSR and
post-processing). The 17 resolved CDN resources all share the exact
`https://cdn.jsdelivr.net/npm/three@0.187.0/` prefix; the missing export is gone.
The only console resource errors are the intentionally blocked font and the
deliberate HTTP 503 replacement test. Startup/daylight, all terminal routes,
question/explanation/four- and five-question completion, and night captures were
saved; the startup, explanation, completion and night images were inspected.

An additional smoke check loaded `/tmp/city-hotfix-review-package` with its
original `main.js` and original continuous animation loop, without inserting the
test observation/frame-step hooks. It rendered the city with Three.js revision
187, hid the loading overlay and reported zero page-script errors. The sole
console resource error was the deliberately blocked font. Its screenshot uses
Playwright's `animations='disabled'` to finish the existing CSS fade reliably on
software GPU; this does not change the shipped HTML/CSS/JS. The full-workflow
package differs from this final package only by the failure message's max-width
assignment, covered independently by the final package's native startup tests.

Browser accommodations: Linux Chromium 154.0.8037.57, software Vulkan/SwiftShader,
real WebGPU backend and actual unmodified production renderer/TSL/SSR pipeline.
Test-only instrumentation provides deterministic production-frame stepping and
observability. When the environment proxy is present, verified-TLS Python fetches
and an exact URL-keyed local cache supply the unchanged CDN response bytes to
Chromium. Fonts are intentionally blocked and use existing system fallbacks.
Synthetic YouTube/Form actions are intercepted before provider contact; they
do not prove real video playback or Form submission. These checks establish
compatibility in this test environment, not Windows hardware-GPU performance,
FPS, school-network CDN access or physical Chrome/Edge acceptance.

Local evidence is outside Git: `/tmp/city-hotfix-investigation/` contains the
original failure screenshot, browser console and network hashes; `/tmp/city-hotfix-*.log`
and `.tap` contain regression logs. Browser output directories contain
`results.json` and screenshots; full-city runs also produce `cdn-resources.json`.
The uninstrumented final-package smoke evidence is in
`/tmp/city-hotfix-live-browser/`.
No real coursework or student information is used.

## Windows 11 Chrome / Edge instructor acceptance

Record browser versions and GPU/driver, then repeat in both browsers using the
candidate over localhost HTTP or the approved HTTPS test host:

1. Reload with cache disabled once, then normally. Confirm loading finishes,
   Manhattan and traffic render, and no missing export, shader error or device
   loss appears in DevTools. Check all four import-map URLs use `0.187.0`.
2. Walk, drive/brake, cycle, fly/ascend/descend; use all 11 cameras. Open/search
   the map, teleport, and Return to Start. Check traffic, collisions and audio.
3. Switch golden/midday/twilight/midnight; compare sky, shadows, reflections and
   post-processing with the accepted city appearance. Record visual anomalies.
4. Reach each fixed terminal and press X. Check Demo retries retain passes;
   dialogs pause movement and close cleanly. Check existing proximity rules.
5. Use the existing synthetic fixture review server for v1 and v2. Verify four/
   five questions, Q05 visibility, single-label acceptance, explanation gates,
   4/4 or 5/5 Form unlock, and cancelled/failed replacement retaining progress.
   Provider tabs are intentionally mocked with `--review-browser`; do not claim
   these tabs prove real course URLs work.
6. Block a Three.js build request in DevTools and reload: a readable failure
   replaces the spinner. Remove the block and reload: startup recovers.

```powershell
py -3 -m http.server 8000 --bind 127.0.0.1
# Separately, use the existing fixture reviewer; repeat with --version 1
# and with --review-browser msedge:
py -3 tests/serve_assignment_fixtures.py --version 2 --prefix course/city --review-browser chrome
```

Physical Windows acceptance is pending; do not merge or release on the strength
of software Vulkan alone.

## Deployment and rollback plan (not executed)

After instructor review, Windows acceptance and explicit merge/release/deployment
authorization, use the existing `tools/package_release.py` mechanism to create a
fresh directory. Verify 47 runtime files, empty manifest, root `index.html` and
both notices; zip its contents and compute a new SHA-256/checksum file. Validate
the candidate under an HTTPS nested path, including JS/JSON MIME, 404s and CDN
access. Assign a new patch version if a release is later approved; do not change
the `v1.0.0` tag, assets or notes in this hotfix task.

Privately back up the deployed website and real assignment files outside the
public directory. Stage the complete candidate in a separate version directory,
preserve the approved course files, verify it, then switch the entry point during
an agreed maintenance window. Use the existing unit-first/manifest-last rules
when course data needs publishing; no such publication is part of this change.

For source rollback, revert the hotfix on a new review branch; never force-push
or move the old tag. The original v1.0.0 website still uses floating `@dev`, so
restoring its HTML can restore the same startup failure: it is a historical
source anchor, not an assured functioning dependency rollback. Prefer the last
instructor-verified complete website/dependency snapshot, if one exists. If only
the added failure message regresses, revert that observer while retaining the
validated fixed dependency URLs. Confirm startup and coursework after any rollback.

Stop at a Draft PR. No merge, release, university deployment or coursework
publication is authorized by completion of these automated checks.
