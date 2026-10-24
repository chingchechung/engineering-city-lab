# Phase 4 — static release candidate

Prepared 2026-10-24 (Asia/Taipei), on `feature/phase-4-release-preparation`.
GitHub PR #4 was verified **merged**, with current main exactly
**dba670bcbf483affad148ace04194089870e9e47**; fetched `origin/main` matched before
branching. No direct main commit, merge, release or deployment is performed.

The instructor reports **11/11 Windows 11 Phase 3 acceptance checks passed**.
This is instructor-reported evidence, separate from automation. Browser versions,
physical GPU observations and FPS were not provided. Phase 4 physical/Apache
acceptance remains pending.

## Delivered boundaries

- Freeze accepted functionality. All 40 runtime JavaScript modules, both existing
  stylesheets, schemas, validated assignment files and city/geographic inputs are
  unchanged. No physics, camera, rendering, maps, dependency, teacher GUI, assignment
  schema or gameplay changes. No new application dependency, build or backend.
- Add only a visible OSM/NYC credit with local licensing/data information, through
  one HTML aside and a separate small stylesheet. The credit remains visible above
  full map and in clean view. It links the full local notices and machine-readable
  geographic database without moving existing controls. No input listener is added.
- Add reproducible static packaging and read-only CI validation. Package discovery
  follows the reviewed local module/style graph, not recursive directory copies.
  It excludes everything outside that graph and the explicit manifest/notices.
- CI runs Node, Python parity, syntax, schema/manifest/runtime integrity and six
  release-specific tests on Ubuntu 24.04 / Node 24 / Python 3.12. Versioned official
  checkout/setup actions use Node 24; jsonschema 4.26.0 is test-only. No deployment
  token, publishing permission, secrets, automatic release or deployment job.
- Document manual Apache HTTPS installation, nested paths/MIME/404 handling,
  dependency limits, teacher export/validate/unit-first/manifest-last publication,
  privacy, rollback and remaining Windows/server/media review.

## Verification

Environment: Node **24.19.0**, Python **3.12.14**, jsonschema **4.26.0**, Linux
Chromium **154.0.8037.57** / Playwright. Baseline before any changes:

```sh
node --test --test-reporter=tap tests/*.test.cjs tests/*.test.mjs
```

**189/189 passed**, zero failures/skips/cancellations, **39.452 s**. Final same
suite: **189/189 passed**, zero failures/skips/cancellations, **55.699 s**.
The existing Node tests were not rewritten or weakened.

```sh
python3 -m unittest tests.test_assignment_contract tests.test_release -v
python3 tools/check_release.py --syntax
python3 tools/check_release.py
```

**11/11 Python tests passed** (five unchanged contract tests plus six meaningful
release tests) in **1.573 s**. Parity remains **364 validation cases and 76 answer
selections**, with exact JS/Python errors, normalization, patterns and schema
agreement. Release tests compare two package builds byte-for-byte, exercise
private/fixture/backup exclusion, reject existing/overlapping destinations,
unsafe/missing inputs, file/directory symlinks and malformed/nonempty manifests,
and serve the real generated package under `/~username/engineering-city-lab/`.
Every packaged file's HTTP bytes and JS/CSS/JSON MIME types pass, including
redirect/direct root/refresh, UTF-8 unit JSON in an isolated test copy and real
404s for missing/publicly excluded paths. No real package or repository receives
fixtures from those tests.

Syntax passed for **66 JavaScript and 15 Python files**; all three schemas,
the empty public manifest and runtime package integrity pass. All **39 local
Markdown link targets** resolve, the exact 18-file report inventory matches Git,
and whitespace checks pass. Runtime/data/schema/fixture preservation and the
Three.js import-map block were independently compared byte-for-byte to the
reviewed main. The reference checkout stays clean at `70cc35d`.

Hosted GitHub Actions also passed all setup and required test steps on
`39a2d58`: [regression run 40093349558](https://github.com/chingchechung/engineering-city-lab/actions/runs/40093349558).
The final PR head's live check is verified again after the evidence-only update.

```sh
python3 tests/browser_learning_dom.py --output /tmp/city-phase4-dom
python3 tests/browser_release.py --site-root /tmp/engineering-city-lab-release --output /tmp/city-phase4-static-browser
python3 tests/browser_education.py --workflow --base-path course/city/ --site-root /tmp/engineering-city-lab-release --output /tmp/city-phase4-browser
```

The unchanged native-DOM suite passed **three groups**, with **three native
external actions**, exact intercepted URLs, no opener/referrer, preserved dialog/
progress and rapid/delayed-close regression coverage. Zero page-script errors.

The new static-browser suite passed **three groups** at an actual physical
tilde-prefixed nested directory: directory redirect/direct `index.html`/reload,
native assignment module and empty-manifest fetch, attribution bounds/hit testing
at 1280×800 and 390×844 in city/clean/full-map views, and keyboard opening of the
packaged license page with no opener and a relative geographic database link.
It does not initialize a renderer and blocks external requests.

The full-city package run passed **all 19 check groups** with **six explicitly
activated external tabs**, zero page-script errors and no GPU device loss.
Demo, v2 four-question and v1 five-question completion, single-label answers,
retry/review, optional explanations, Form unlocking, small viewport, full-map Form,
failed/cancelled/stale load preservation, successful replacement cleanup, Return,
mode/camera changes and original map/preset teleports all passed. Normal walking
reached all five unchanged sites in 84.49 / 11.46 / 67.68 / 143.91 / 135.30 metres,
all under 250 m. The two expected console resource failures are the deliberately
blocked font and deliberate HTTP 503 test case.

It served HTML/CSS/modules from the generated **47-file candidate**, including
main instrumentation from that package, while synthetic assignments remained
browser test routes from the test checkout. No test file is packaged. The
explanation/four-question/mobile-HUD/five-question and attribution captures were
inspected; the original city and prominent completion Form remain readable.

All synthetic provider requests are intercepted before any contact. Full-city
software Vulkan, deterministic production-frame stepping and cached exact CDN
responses are unchanged test accommodations. Font access is deliberately blocked
in cloud and existing fallbacks are used; this is not evidence of Google Fonts
availability. No physical Windows results, live media/submission verification,
hardware GPU throughput or FPS measurements are inferred.

A separate current-network probe fetched the original Three.js webgpu/tsl builds
and BufferGeometryUtils addon via normal verified TLS: all returned HTTP 200,
JavaScript MIME types and bytes matching the browser test cache. Exact response
hashes are in `/tmp/city-phase4-cdn-probe.json`. This limited probe confirms those
three resources at this time, not an immutable full dependency snapshot, future
CDN availability or access from the university network.

## Package and evidence

```sh
python3 tools/package_release.py --output /tmp/engineering-city-lab-release
```

Generated candidate: **47 files**, **2,604,058 content bytes** (about 2.6 MiB on
disk), no archive committed.
All bytes match their source; repeated build inventory/content is identical.
Contents are index, 40 modules, three stylesheets, the empty public manifest and
two notices. The public assignment directory contains only `manifest.json` with
`{"schemaVersion":1,"units":[]}`. No fixture, draft, backup, credentials, student
record, test output or unnecessary development file is included. Package
allowlisting/exclusion and source review establish this distribution boundary;
this is not a claim of an exhaustive security audit.

Logs/evidence remain outside Git: `/tmp/city-phase4-baseline.tap`,
`/tmp/city-phase4-final.tap`, `/tmp/city-phase4-python.log`, `/tmp/city-phase4-dom/`,
`/tmp/city-phase4-static-browser/`, `/tmp/city-phase4-browser/` and their associated
`.log` files. Reproduce with [deployment commands](deployment.md#regression-and-ci).
The complete package file/size/SHA-256 inventory is
`/tmp/city-phase4-package-inventory.json` and `/tmp/city-phase4-package.sha256`.
The package is local only and has not been uploaded anywhere.

## Exact changed files

The Phase 4 diff contains **18 files**:

| File | Reason |
| --- | --- |
| `.github/workflows/regression.yml` | Minimal PR/manual regression CI with read-only permissions. |
| `AGENTS.md` | Phase 4 authorization, verified baseline, reported acceptance and preservation/review gate. |
| `Plan.md` | Reviewed Phase 3 and approved release milestones/evidence. |
| `README.md` | Project entry, local use, links to deployment/publication and license/privacy limits. |
| `THIRD_PARTY_NOTICES.html` | Distributed city/Three.js/OSM/NYC/font/assignment notices and geographic database access. |
| `css/attribution.css` | Small visible attribution in normal/clean/full-map views. |
| `docs/deployment.md` | Reproducible package, traditional Apache, regressions, dependency/privacy and rollback instructions. |
| `docs/phase-3-results.md` | Later PR #4 merge and instructor-reported 11/11 evidence. |
| `docs/phase-4-results.md` | This implementation/evidence/inventory and release limits. |
| `docs/release-checklist.md` | Candidate gates and final physical Windows/Apache/content checks. |
| `docs/teacher-publishing.md` | Existing GUI exports, validation, manual publication/update/removal and public-answer boundary. |
| `docs/upstream.md` | Attribution/license audit, corrected NYC terms source and separately reviewable pinning recommendation. |
| `index.html` | Add attribution stylesheet/aside only; original import map and UI remain. |
| `tests/browser_education.py` | Optional package root for the unchanged full-city learner regression. |
| `tests/browser_release.py` | Real nested native-browser package/attribution/notice checks. |
| `tests/test_release.py` | Six package/privacy/path/HTTP regression tests. |
| `tools/check_release.py` | Read-only syntax/schema/static-manifest/runtime integrity checks. |
| `tools/package_release.py` | Standard-library clean runtime-graph packaging with empty-manifest gate. |

## Remaining public release gates

No release/deployment has been performed. The draft PR is a reviewable candidate,
not a declaration that every production gate has passed.

1. Instructor reviews the Phase 4 diff and [release checklist](release-checklist.md).
   Complete final physical Windows Chrome/Edge and real university HTTPS Apache
   nested-path/MIME/404/CDN checks. No university server credentials or deployment
   destination were provided or used. HTTP-only production cannot supply normal
   WebGPU secure context and remains a deployment blocker until HTTPS is available.
2. Retain data/license notices and free machine-readable geographic access.
   Confirm any additional NYC dataset/entity distribution terms; code MIT does
   not replace ODbL or NYC conditions. The visible OSM credit and Three.js
   ported-code notice address verified omissions in the imported distribution.
3. Existing floating Three.js `@dev` URLs prevent immutable external-dependency
   reproduction. They are deliberately unchanged by instruction. The dependency-
   only snapshot recommendation in [upstream](upstream.md#phase-4-release-audit)
   requires separate approval and physical comparison; no offline bundle is added.
4. Before real units are published, instructor verifies actual video availability,
   content/language and Google Form access/submission settings. Public JSON answers
   are visible, progress is memory-only and Google Forms does not report submission
   back to this app. No real course content was used or published here.

Stop at the new **draft PR** for review. Do not merge, create a GitHub Release,
deploy to any server, publish real assignments or begin another phase.
