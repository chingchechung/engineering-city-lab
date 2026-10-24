# Release candidate review

Prepared 2026-10-24 (Asia/Taipei). Phase 3 PR #4 merged at verified baseline
`dba670bcbf483affad148ace04194089870e9e47`. The instructor reports **11/11
Windows 11 Phase 3 acceptance checks passed**. Browser versions, GPU observations
and FPS were not supplied; that report is separate from Phase 4 automation.
See [Phase 4 results](phase-4-results.md) for final commands, evidence and inventory.

## Candidate gates

- [x] Existing 189 Node regressions pass before and after changes.
- [x] Python v1/v2 validation/normalization/schema/answer parity passes.
- [x] Native dialog and explicit secure video/explanation/Form actions pass.
- [x] Static-only package reproduces identical local bytes and excludes private,
  fixture, development and credential files; default manifest is empty.
- [x] Packaged files pass real nested HTTP MIME/404/UTF-8/redirect checks.
- [x] Native Chromium nested module/manifest loading, direct navigation/refresh
  and attribution/license accessibility pass, including a tilde-prefixed path.
- [ ] Full-city packaged learner regression: final outcome in the Phase 4 record.
- [x] Lightweight CI commands pass locally; workflow has no publishing permission.
- [ ] Hosted GitHub Actions result: final outcome in the Phase 4 record.
- [x] Apache installation, teacher publication, source/license/data attribution,
  public answers, in-memory progress and external dependency limits documented.
- [ ] Instructor reviews the draft Phase 4 PR and license/data-source conditions.
- [ ] Instructor performs final physical Windows/actual HTTPS Apache checks below.
- [ ] Instructor verifies actual course media and Form settings before any real
  assignment publication. Empty-manifest candidate has no published course units.

The candidate can be prepared while public deployment acceptance remains pending.
Do not describe unchecked physical/server/content gates as passed or automatically
publish, merge or create a GitHub Release. An HTTP-only production origin, wrong
MIME types, CDN failure, or a failing regression is a deployment blocker.

## Final Windows 11 Chrome and Edge checks

Record actual browser versions, OS, device/GPU observations and console errors
when observed. No FPS benchmark is required or inferred. Repeat in both browsers.

1. Serve the generated package over loopback HTTP at a nested path first. On the
   intended **HTTPS Apache URL**, check direct `index.html`, directory/trailing-slash
   navigation and refresh, secure context/WebGPU availability, correct MIME types
   and true 404 for a missing `.js`/`.json`. Check loading with the actual network's
   CDN policy; verify system font fallback if fonts are blocked.
2. Confirm the empty assignment list and Demo Mode. Check fixed start, all five
   fixed sites, X, retry/reopen/pass progress and no demo video/Form links. Refresh
   resets only the in-memory attempt; unrelated sound preferences remain.
3. Compare original city appearance and loading; walking, car, bicycle, helicopter;
   ground switches, independent flight, traffic/pedestrians, collisions, all camera
   modes, lighting/shadows and audio. Check minimap/full map, search, GPS, preset
   and map teleports, Return to Start and clean view. Progress survives travel.
4. Check the small geographic credit in normal/clean/full-map views at desktop
   and a smaller viewport. Follow **Licenses & data** by keyboard: the local notice
   opens separately, has no opener, and its geographic data link resolves under
   the site's nested directory. Check text is readable and controls stay usable.
5. For synthetic units, use only the controlled Chrome/Edge review mode from
   [Phase 3 instructions](phase-3-results.md#windows-11-chromeedge-manual-acceptance).
   Do not upload fixtures to Apache or follow dummy links in an ordinary browser.
   This harness serves the checkout, while the package-specific cloud regression
   exercises the same byte-identical modules from the candidate.
6. Check v2 four-question S01 and five-question S02; repeat legacy v1. Choose one
   accepted label, try wrong/retry, revisit passed questions, verify explanation
   access and optional text. Native question links appear before choices; there
   is no automatic tab or viewing requirement. Verify paused city, Tab, Escape,
   Close, held-key cleanup and return from intercepted video/Form tabs.
7. Verify Form unlocking only at 4/4 or 5/5, HUD/dialog access after closing and
   over full map, no exit requirement. Travel and failed/cancelled switches keep
   progress/Form; successful confirmed replacement clears stale resources, resets
   question progress and preserves position. Four-question units leave Q05 inactive.
8. Instructor-only real publishing acceptance: validate actual GUI exports and
   follow [unit-first, manifest-last publication](teacher-publishing.md). Verify
   real videos' content/language/access and actual Form restrictions/submission
   settings. The app cannot confirm Form submission. Remove public files when
   direct access must end; unlisting alone is insufficient.

Report any failures with reproduction, actual versions and screenshots if useful.
Physical touch/gamepad hardware and performance should only be marked verified
if actually tested. Preserve the accepted city and stop for review before any
further implementation work.
