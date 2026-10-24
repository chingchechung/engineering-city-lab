# Engineering City Lab — development rules

These rules apply to this repository and its subdirectories. Read `Plan.md` and
the linked Phase 0 records before making changes. The user's current instructions
take precedence over historical plans and rules from other projects.

## Current authorization

- Phase 0 is preparation and documentation only. Do not implement terminals,
  assignment loading, grading, progress, overlays, spawn changes, or new controls.
- Stop after Phase 0 for instructor review. A plan for a later phase is not
  authorization to implement it. Record subsequent explicit approvals in `Plan.md`.
- Work on a separate development branch. The imported baseline on `main` is
  `cca9c12a096951d63fee1d26904c04be0a128cef`. Do not commit directly to `main`,
  merge, force-push, replace history/tags, deploy, or update upstream automatically.
- Phase 0 must leave every imported file byte-identical, including tests, HTML,
  CSS, generated geography, tools, dependencies, and license notices.

## Product constraints for later approved work

- Extend the existing city. Preserve its geography, buildings, graphics,
  vehicles, traffic, pedestrians, physics, audio, four travel modes, eleven
  cameras, HUD, minimap, full city map, search, waypoints, and teleport behavior.
- Keep the existing Three.js import map, WebGPURenderer, TSL materials, lighting,
  shadow system, SSR/bloom pipeline, culling, and dependency sources unchanged.
  Pinning the floating `@dev` dependency needs a separate reviewed change.
- Add exactly five fixed terminal locations near the original taxi start, with
  stable terminal IDs and a fixed educational starting position. Do not derive
  them from camera position, randomness, saved travel state, or unit content.
- Reserve **X / `KeyX`** for question interaction. Preserve E/Space for ascent,
  Q/C for descent, V for camera cycling, M/Escape for maps, and existing controls.
- Wrong answers allow retry. They must not clear passed answers, move the player,
  replace the city, or reset a unit. Teleporting or switching cameras/modes must
  not erase educational progress.
- No shrinking maze, randomized course map, map timer/budget, countdown, exit
  station, or travel requirement for completion. Keep the full map and teleports.
- Support the established four- or five-question units without changing their
  JSON contract. Five physical sites do not make Q05 mandatory for a four-question
  unit; keep the fifth site fixed and inactive for that unit.
- Separate assignment/session state from the city and rendering systems. Use
  small additive modules and a narrow composition point in `js/main.js`.
  Do not transplant the maze game, its rendering, or its failure/reset policy.

## Assignment compatibility and content

- The reference is `chingchechung/ece_hw_webproject`, inspected at
  `70cc35d9ce828bcd5357f16fe85f303aa2d30cd9`. Read
  `docs/assignment-compatibility.md` before any later port.
- Units are exactly S01–S12, filenames Sxx.json, question IDs sequential Q01–Q04
  or Q05. Keep option order, supplied language, version fields, URLs, and precise
  validation errors. No implicit v1/v2 migration or invented course content.
- V1: four options and `correctOption`. V2: three/four options and a nonempty,
  distinct `correctOptions` array. Students choose **one** label in either
  version; any accepted v2 label passes. Never require selecting all labels.
- The public manifest stays version 1 and is the allowlist. Request only unit
  files it names; never guess unpublished filenames. Validate before replacing
  an active unit, and preserve it on cancellation or failed loading.
- Keep the static-site model. No backend, login, telemetry, student identifiers,
  score collection, or automatic publication. Teacher authoring remains local;
  instructor uploads validated public files manually.
- Keep private drafts, unpublished answers, and authoring backups out of public
  directories and Git. Before adding authoring data, add suitable ignores such as
  `teacher_data/` and `export/`; Phase 0 adds no such data or runtime files.
- Use safe DOM APIs for question text. Validate supported HTTPS video/Form links;
  explicit user actions open them with `noopener noreferrer`. Google Forms
  controls submission availability. Static JSON answer keys are public data.

## Integration and verification discipline

- Treat the coordinates in `docs/architecture.md` as proposed survey locations,
  not visually verified placements. Validate them against actual buildings,
  street props, sidewalk traffic and all relevant cameras before freezing them.
  Adjust the terminals, not the city; do not relocate them dynamically at runtime.
- Existing `nyc-player-state` restores positions. A later approved educational
  entry must deliberately take precedence over that restore to guarantee its
  fixed start. Preserve the unrelated `nyc-sound` preference.
- A new modal needs coordinated keyboard, pointer, touch and gamepad ownership.
  Clearing input once is not a pause: controllers coast and traffic can collide.
  Do not let camera/mode/map listeners operate through an answering dialog.
- Preserve existing tests. When an approved module addition changes the explicit
  29-module preload inventory, update its exact expectation and the preload list
  together; do not remove the boot regression checks merely to make tests pass.
- Run the imported baseline suite from the repository root:

  ```sh
  node --test --test-reporter=tap tests/*.test.cjs tests/*.test.mjs
  ```

  Node 24.19.0 passed all 105 tests in Phase 0. The geodata test needs substantial
  memory and subprocess execution; Overpass tests use mocked curl, not the network.
  See `docs/baseline-tests.md` for coverage, environment restrictions and limits.
- Add meaningful behavior tests with approved features, including retries,
  proximity, input focus, unit switching and preservation. Do not add placeholder
  educational implementations or tests during Phase 0.
- Preserve MIT attribution, geographic-data attribution and third-party license
  obligations described in `docs/upstream.md`. Do not relabel all data as MIT.
- Report exact changed files, commands/results, untested platforms, limitations
  and the next review gate. Keep instructor-reported Windows success separate
  from Linux automated checks; never infer GPU performance from unit tests.
