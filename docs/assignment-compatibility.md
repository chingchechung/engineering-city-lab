# Future S01–S12 assignment integration boundary

Phase 0 reference inspection only; no schema, loader, question or answer data has
been copied into the city repository.

Source: [chingchechung/ece_hw_webproject](https://github.com/chingchechung/ece_hw_webproject),
`main` at **70cc35d9ce828bcd5357f16fe85f303aa2d30cd9**, subject
“Record verified v1.0.0 release and publication evidence.” The GitHub main ref
was checked against the local reference checkout. Use this commit when reviewing
the future port, not an unspecified moving branch.

## Source of truth to reuse

| Reference files | Intended use |
| --- | --- |
| `schemas/assignment-v1.schema.json`, `assignment-v2.schema.json`, `manifest-v1.schema.json` | Exact published data contracts. |
| `js/assignment-rules.js`, `js/assignment-validator.js` | Pure browser/Node URL rules, normalization, versioned validation and `acceptsAnswer`. The `student/js/` copies match these files byte-for-byte at the inspected revision. |
| `tools/assignment_data.py`, `tools/validate_assignments.py` | Python contract implementation and read-only validation CLI; use for parity when porting. |
| `student/js/assignment-loader.js` | Allowlist loading, cancellation/generation checks, error handling and validation-before-replacement patterns. Its DOM IDs, callbacks and maze-specific copy cannot be copied unchanged into the city. |
| `tests/contract_cases.py`, `contract_cases_v2.py`, `test_assignment_data.py`, `test_assignment_v2.py`, `browser_validation.py`, `validate_in_js.cjs` | Version/normalization/URL/answer and cross-language validation evidence to carry over or adapt in an approved phase. |
| `tests/fixtures/`, `tests/fixtures/v2/` | Synthetic four/five-question v1/v2 units and version-1 manifests; future tests only, never course publication. |
| `tools/assignment_editor*.py` and source documentation | Existing local teacher-authoring workflow; do not rebuild it as a city feature. |

Some earlier reference documents still describe integration as pending. The
inspected revision's current schemas, validator, loader and release/test records
are more recent evidence. Phase 0 did not rerun that separate project's release
suite; the city's 105 baseline tests are not proof of JSON integration.

## Exact public contract

| Rule | Assignment v1 | Assignment v2 |
| --- | --- | --- |
| Explicit `schemaVersion` | Number 1 | Number 2 |
| Unit fields | `schemaVersion`, `unitId`, `title`, `googleFormUrl`, `questions` | Same |
| Unit IDs and filenames | S01–S12; exact matching Sxx.json basename | Same |
| Question count and IDs | 4 or 5; sequential unique Q01–Q04/Q05 | Same |
| Required question fields | `id`, `questionVideoUrl`, `explanationVideoUrl`, `options`, `correctOption` | Same except `correctOptions` replaces `correctOption` |
| Optional question fields | `title`, `prompt`, `explanationText` strings | Same |
| Options | Four nonblank strings, A–D in original order | Three or four nonblank strings, A–C/A–D in original order |
| Accepted answer data | One label in `correctOption` | Nonempty distinct array of existing labels in `correctOptions` |
| Student choice | Exactly one label | Exactly one label; membership in accepted labels passes |

V2 `["A", "C"]` means A **or** C passes. It does not require selecting both.
No hidden D is created for three choices. Reject mixed version/answer fields,
unknown properties, bad IDs, invalid answer labels and unpublished/incomplete data.
Keep normalization behavior and option order; never silently migrate versions.

The public manifest remains **schemaVersion 1**, with `units` entries containing
exactly `unitId`, `title`, `file`. Its units are an allowlist, not twelve filenames
to probe. Both v1 and v2 assignments can be named by this same manifest format.
An empty list is valid; the reference's public manifest is empty by default.

Preserve exact supported HTTPS YouTube/Google Forms URL validation, including
placeholder rejection; do not replace it with a loose “starts with https” check.
Serve only explicitly published JSON from relative `assignments/` paths. A future
loader must work under an Apache/GitHub Pages subdirectory, handle network/parse/
validation failures, suppress stale responses, and commit a switch only after
the replacement unit validates and the user has confirmed replacement.

## City-specific behavior and reuse exclusions

| Area | City rule |
| --- | --- |
| World/start | Existing complete city; fixed start near the original taxi; five fixed T01–T05 sites. No map generation. |
| Question mapping | Q01→T01 through Q05→T05, independent of unit and JSON version. Four-question units leave T05 present but inactive and not required. |
| Interaction | X; preserve original city mode/camera/flight/map keys. |
| Incorrect answer | Feedback and retry at the same question. All previously passed IDs, player location and terminal sites remain unchanged. |
| Correct answer | Mark only that question passed; repeat visits must not revoke progress. |
| Travel | Camera/mode changes, minimap/full map, preset/map teleportation do not alter passed IDs. |
| Completion | All questions in the active unit passed; offer its Google Form immediately. No exit or travel requirement. |
| Maps | Existing full map/search/waypoint/teleport functionality remains, with no timer or usage budget. |
| Unit replacement | Explicit confirmation, then validate-before-commit; cancellation/failure preserves current progress. A new unit may reset educational state deliberately, never because an answer was incorrect. |
| Persistence | Proposed in-memory session state initially. Do not reuse travel localStorage as assignment progress or add student tracking. |

Reuse validation and content semantics, but exclude the reference game's shrinking
maze, wrong-answer reset, randomized placement, 30-second map budget, exit unlock,
Lite/3D renderers, vehicle physics and E interaction. Its loader text about reset
of maze/map allowance also needs replacement. A compatible JSON consumer does
not need compatible maze gameplay.

Recommended module boundary for later work: a pure validated assignment model
and answer helper, a loader, a session store keyed by `unitId`/question ID, a
fixed city-terminal adapter and a scoped DOM interaction view. Keep the city
controllers, traffic, map and rendering independent of answer correctness.
Before selecting another unit, record a reviewed policy for whether its deliberate
new session also reapplies the fixed start. This does not affect ordinary travel
or retry behavior and is not implemented in Phase 0.

## Authoring, privacy and publication

Keep local offline teacher editing and explicit validated exports. Do not import
private drafts, the instructor's unpublished reference questions/answers, retained
Q05/D authoring metadata or example URLs as public content. No upload/sync service,
backend, authentication, grades or telemetry is needed. Before copying code,
record its reuse permission and applicable notices as described in `upstream.md`.

Future student UI should use safe text rendering, open the question video on
request, offer the optional explanation after a correct answer, and expose the
Form only after all required questions pass. Google Forms owns submission
availability. Client-side JSON answers are visible by design and are not a
secure examination/grade-submission system.
