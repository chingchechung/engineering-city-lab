# Phase 3 — complete educational workflow

Prepared 2026-10-24 (Asia/Taipei) on `feature/phase-3-learning-workflow`, from
verified latest main **1a362c95fb073b7652028ba47388185936d1cf02**. GitHub confirmed
PR #3 was merged at that commit before this branch or implementation was created.

The instructor reports **9/9 Windows 11 Phase 2 acceptance checks passed**.
This is instructor-reported evidence, separate from cloud automation; browser
versions, GPU measurements and FPS were not supplied. Phase 3 physical acceptance
remains a separate review gate.

## Implemented workflow

Explore the existing city → approach a fixed terminal → press X → optionally
open **Watch Question Video** → choose one answer → submit/retry → optionally
open **Watch English Explanation** after passing → complete all four/five
questions → open the unit's **Google Form**.

- The question video appears before the answer choices. All links use the exact
  active validated URL, `target="_blank"` and `rel="noopener noreferrer"`.
  Only native user clicks/keyboard activation navigate. There is no automatic
  opening, embedding, playback framework, timer or proof-of-watching requirement.
- Incorrect answers leave the dialog open and preserve every prior pass, city
  position and mode. Correct answers use the existing session/`acceptsAnswer`,
  update progress/green markers and immediately reveal the question's explanation.
  V2 still accepts one of its accepted labels with a single radio selection.
- Explanation video data remains **required in published JSON**, while watching
  it is optional. Nonblank supplied `explanationText` is displayed with
  `textContent` and preserved line breaks; missing/blank text has no empty text
  section. Reviewing a passed question retains explanation access even after an
  incorrect review. No instructional text is generated.
- The existing `session.complete` alone unlocks the Form: 4/4 excludes inactive
  Q05; 5/5 includes it. The prominent Form link remains in the education HUD after
  closing the dialog, including over the full map. It is also offered inside a
  completed question dialog. Both use the same completion projection, with no
  second counter, exit or location requirement.
- HUD links have pointer events enabled and native keyboard activation. Link
  Enter/Space events do not reach city controls. Question/selector pause, focus,
  Escape and held-key cleanup remain coordinated; leaving for another tab never
  closes the question dialog or changes assignment progress.
- A queued close event from an earlier opening is ignored once the question
  dialog has reopened. The focused native-DOM regression verifies rapid question
  changes and delayed close delivery cannot clear the new answer interaction.
- Confirmed valid replacement clears previous question/explanation/Form URLs
  and starts the new question attempt without moving the city. Failed, cancelled
  or stale loading preserves the old completed unit and Form availability.
- Demo Mode keeps its original five synthetic questions, retry/progress and
  completion message, with no video/explanation/Form URLs. The real public
  manifest is still empty, and no course or fixture units are published.

The app does not autoplay/download videos, track viewing or Form submissions,
collect student data, store progress across reloads, add backend services or
change the teacher GUI. Google Forms controls submission acceptance. No Phase 4
work or deployment is included.

## Preserved boundaries

The Phase 2 validator/rules, native adapter, loader, session, schemas and all 15
reference copies remain byte-identical. No JSON fields or validation/answer
semantics change. The pinned reference remains
`ece_hw_webproject@70cc35d9ce828bcd5357f16fe85f303aa2d30cd9` and its checkout is
unchanged; [reuse notices](assignment-reuse.md) remain applicable.

The fixed start, five terminal coordinates, 3/18/8 m radii, stationary/obstruction
checks, X, ground-mode switching, helicopter behavior, Return to Start, maps,
cameras, traffic, physics, graphics and original assets are preserved. Three.js
URLs/import map, original city CSS and renderer remain unchanged. The preload
inventory stays at 40; no runtime dependency or module is added.

## Verification

Before changes: **171/171 Node baseline tests passed**, with zero failures,
skips or cancellations, in **57.977 s**, on Node **24.19.0**.

After implementation: **189/189 Node tests passed** (171 existing + 18 new), with
zero failures/skips/cancellations, in **40.066 s**. The new tests cover exact URL
projection for both versions, pre/post-pass explanations, missing/blank/literal
text, wrong reviews, single accepted v2 labels, four/five completion, old-question
identity rejection and successful/failed/cancelled/stale replacement resources.

The unchanged Python suite passed **5/5** in **0.538 s**, including exact
JavaScript/Python/JSON Schema agreement across **364 validation cases** and
**76 answer selections**. No cases were skipped.

The focused native-DOM browser regression passed **3 check groups**, including
three real external actions (question click, explanation Enter, Form Enter),
exact URLs, no opener/referrer, retained dialog/progress and all four answers
through rapid reopening and simulated delayed close delivery. It uses the real
HTML/modules and session without a city renderer; this evidence is separate
from the full-city rendering check.

The final full-city run passed **19 check groups** on Linux Chromium
**154.0.8037.57** under **`/course/city/`**, including all existing city/demo/
assignment checks. It completed v2 four-question and v1 five-question workflows,
retry/review, optional/missing/blank/literal explanation text, 4/4 and 5/5 Form
unlocking, stale-link cleanup, failed/cancelled replacement preservation, travel,
full-map Form activation and a 390×844 HUD check. **Six native external actions**
used actual mouse/Enter activation; every navigation was intercepted, had no
opener/referrer, and preserved the city/session/dialog as applicable. No automatic
video or Form navigation occurred.

The final result log contains **zero page-script errors or GPU device loss**.
Expected resource errors came from the deliberately blocked font and HTTP 503
failure case. Question/explanation, literal text, small HUD, green completion
marker and five-question Form screenshots were inspected. Evidence stays outside
Git at `/tmp/city-phase3-evidence/`: `results.json`,
`learning-external-actions.json`, `assignment-requests.json`, the existing city/
assignment captures, `learning-explanation.png`, `learning-small-hud.png` and
`learning-five-complete.png`. The separate focused DOM evidence is at
`/tmp/city-phase3-dom-evidence/`.

Automated evidence does not establish physical Windows Phase 3 acceptance, native
Chrome/Edge headed-review behavior on that platform, live English video content,
playback, provider availability or actual Form submissions. Real touch/gamepad
hardware and hardware GPU performance were not verified.

Syntax checks passed for **66 JavaScript** and **11 Python** files; local Markdown
links, the exact **16-file** report inventory and `git diff --check` passed. Both
versions of the unchanged default loopback fixture-serving behavior passed nested
HTML/module, manifest/unit and unpublished-unit 404 smoke checks. The public
manifest remains empty. All 15 pinned reference copies, the Phase 2 adapter/
loader/session, terminal configuration/navigation/markers, demo fixtures and
original city CSS/preload test are byte-identical to the reviewed baseline.

Commands from repository root:

```sh
node --test --test-reporter=tap tests/*.test.cjs tests/*.test.mjs
python3 -m unittest tests.test_assignment_contract -v
python3 tests/browser_learning_dom.py --output /tmp/city-phase3-dom-evidence
python3 tests/browser_education.py --workflow --base-path course/city/ --output /tmp/city-phase3-evidence
```

The Node suite and Python parity subprocess require subprocess access. Python
contract tests use test-only `jsonschema`; browser tests use Playwright/Chromium.
The app itself retains its static native-module deployment with no install/build
step. The browser harness still uses the full original city and production
movement/physics/render callback, with test-only observations and deterministic
frames to bound software Vulkan work. Intermediate route draws may be skipped;
movement/collision/traffic/UI still run. Exact cached CDN bytes and existing font
fallbacks are the same cloud test accommodations as Phase 2, not product changes.
No hardware performance or FPS conclusion follows from these captures.

Phase 3 browser tests intercept provider requests at **browser-context level**,
including the first request of a new tab. They fulfill local mock HTML at the
original fixture URL, assert `window.opener === null`/no Referer, and use actual
clicks and Enter activation. No dummy video or Form provider is contacted.
Test-only response mutations exercise literal/missing/blank explanation text
and different unit links; original fixture files remain unchanged and unpublished.

## Exact changed files

The Phase 3 diff contains **16 files**. Production changes stay within the
existing educational HTML/CSS/UI plus one visibility callback in main.

| File | Reason |
| --- | --- |
| `AGENTS.md` | Records merged Phase 2, reported 9/9 acceptance, Phase 3 scope and review constraints. |
| `Plan.md` | Approved workflow milestones, evidence and Phase 4 review gate. |
| `docs/assignment-compatibility.md` | Updates the presentation boundary to the implemented Phase 3 workflow. |
| `docs/assignment-reuse.md` | Clarifies explicit media presentation and mocked fixture navigation; source provenance stays unchanged. |
| `docs/phase-2-results.md` | Records the PR #3 merge and instructor-reported acceptance separately from historical automation. |
| `docs/phase-3-results.md` | This workflow, file inventory, verification, limits and Windows review record. |
| `js/education-ui.js` | Derives safe link/explanation availability from the existing session, clears stale resources and preserves modal handling. |
| `js/main.js` | One visibility callback keeps completed progress/Form accessible when the full map is open. |
| `index.html` | Native question/explanation/Form anchors and optional explanation text section in the existing educational UI. |
| `css/education.css` | Scoped link prominence/focus/pointer styling, safe text wrapping and completed HUD above the map. |
| `tests/learning-workflow.test.mjs` | Eighteen resource/session/replacement regressions using the actual validated model. |
| `tests/browser_learning_workflow.py` | Native new-tab, explanation/completion, stale-link, mobile HUD and map checks with provider interception. |
| `tests/browser_learning_dom.py` | Fast real-DOM link and delayed-close/rapid-reopen regression without loading the city renderer. |
| `tests/browser_assignments.py` | Adds workflow hooks and Form-preservation observations to existing real-city assignment tests. |
| `tests/browser_education.py` | Optional `--workflow` runs the existing city/assignment checks plus Phase 3 checks. |
| `tests/serve_assignment_fixtures.py` | Optional headed Chrome/Edge physical review with mocked provider tabs; normal loopback fixture serving remains. |

## Windows 11 Chrome/Edge manual acceptance

Use the feature branch. Never publish fixtures or follow their dummy provider
URLs in an uncontrolled browser. The review mode below mocks every supported
video/Form host **before** new-tab navigation while using the normal production
city loop and native installed browser, without cloud software-rendering flags.

1. Verify the real empty deployment first: `py -3 -m http.server 8000`, then open
   `http://127.0.0.1:8000/`. Demo Mode must have no video/explanation/Form controls,
   including after all five passes. Assignments reports no published units.
   Check original city/start/navigation behavior, then stop that server.
2. Install test-only Playwright if needed: `py -3 -m pip install playwright`.
   With Chrome installed, run:

   ```powershell
   py -3 tests/serve_assignment_fixtures.py --version 2 --prefix course/city --review-browser chrome
   ```

   The controlled Chrome window opens the nested URL. Repeat with
   `--review-browser msedge` for installed Edge. Record the actual browser
   versions and observations. Closing the city tab stops the review server.
3. Select/confirm S01 (v2, four questions). Verify nearby city position/mode is
   retained and Q05 inactive. Approach a terminal and press X. The question video
   must be above the unchanged prompt/choices. Opening the dialog alone opens no
   new tab. Click Watch Question Video and return: the mock tab must show the
   exact fixture URL, with the question still open and paused in the city.
4. Try a wrong answer first. It must show retry feedback with no new explanation,
   no lost passes and no city relocation. Then answer correctly: S01 v2 accepted
   labels are Q01 A, Q02 B/C, Q03 A/B/C, Q04 A. Choose one radio only. Check green
   markers and immediate progress/explanation access.
5. Open Watch English Explanation using Enter; return and check the dialog,
   selected answer, Tab/Escape/Close and city-key suppression. Explanation viewing
   is optional. Revisit a passed question and try a wrong review: the pass and
   explanation must remain. Inspect original explanation text and option order.
6. Complete S01 at 4/4 without Q05 or an exit. The Form link must unlock only now,
   inside the dialog and in the HUD after Close. Click or press Enter to open its
   mocked tab. Return to the unchanged completed city; no submission is tracked.
7. Try Return to Start, walking/cycling/driving/helicopter, cameras and map/preset
   teleports. Completion/green markers/Form availability must remain. The HUD Form
   must be clickable over the full map. Check an ordinary desktop size and a
   smaller viewport; restore the original window size afterward.
8. Cancel a replacement or take the browser offline during loading: old progress
   and Form must remain. Restore connectivity and successfully confirm S02: the
   new 0/5 attempt must clear old media/Form UI and restore Q05 without moving the
   player. V2 S02 Q05 accepts B or C. Form unlocks only at 5/5.
9. Close the test browser/server and repeat with `--version 1` for legacy four-
   and five-question units with four options, accepted labels A/B/C/D/(A). No
   schema/answer conversion or all-label selection should occur.
10. Automated browser tests additionally exercise absent/blank/literal explanation
    text, distinct replacement links, malformed loads and native focus/input
    checks. Review those results alongside physical observations; do not infer
    live English video content, playback or actual Form submission from mocks.
11. Close review windows and confirm the repository is clean and the real
    `assignments/manifest.json` remains empty. Record Phase 3 physical results for
    instructor review. Real course publication remains a separate instructor step.

Stop at the new draft PR. Do not merge, deploy or begin Phase 4 automatically.
