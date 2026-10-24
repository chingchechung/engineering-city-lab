# Assignment component provenance and reuse

Source: [chingchechung/ece_hw_webproject](https://github.com/chingchechung/ece_hw_webproject)
at **70cc35d9ce828bcd5357f16fe85f303aa2d30cd9** (Engineering Maze Lab v1.0.0
release evidence). The instructor explicitly authorized reuse of these approved
assignment components in the Phase 2 request on 2026-10-24 (Asia/Taipei).
The reference checkout is read-only and remains at that commit.

No root-level LICENSE exists at this reference revision. The reuse permission is
the instructor's explicit project instruction; no blanket MIT license for the
reference application is inferred. Original source headers, schema comments and
synthetic-content labels are retained. The reference's bundled dependency notices
are not a license for its own application, and no bundled third-party code is
copied. Existing city/Three.js/geographic notices remain in force; see
[upstream.md](upstream.md).

## Unchanged copies

Each file below has exactly the source revision's bytes, at the same relative
path in this repository. These can be compared with `git show <revision>:<path>`
in the read-only reference checkout; the implementation report records the check.

| Files | Purpose |
| --- | --- |
| `schemas/assignment-v1.schema.json` | Published v1 contract. |
| `schemas/assignment-v2.schema.json` | Published v2 contract, including three/four choices and accepted labels. |
| `schemas/manifest-v1.schema.json` | Version-1 allowlist contract. |
| `js/assignment-rules.js` | Exact supported URL patterns. |
| `js/assignment-validator.js` | Normalization, ordered error objects, version validation and single-choice `acceptsAnswer`. |
| `tools/assignment_data.py` | Independent Python validation/normalization/answer implementation used for parity. |
| `tools/validate_assignments.py` | Read-only offline validator CLI; no authoring, uploads or publication. |
| `tests/contract_cases.py` | Shared synthetic acceptance/mutation corpus, including v2 cases. |
| `tests/contract_cases_v2.py` | Version-2 and single-selection answer cases. |
| `tests/fixtures/S01.json`, `tests/fixtures/S02.json`, `tests/fixtures/manifest.json` | Test-only v1 four/five-question units and allowlist. |
| `tests/fixtures/v2/S01.json`, `tests/fixtures/v2/S02.json`, `tests/fixtures/v2/manifest.json` | Test-only v2 four/five-question units and version-1 allowlist. |

This is **15 byte-identical files**. Fixtures are never placed in the public
assignment directory. Their example video/Form URLs are validation inputs only;
Phase 2 does not open, embed or present those links.

## Reviewed adaptations

- `js/assignment-contract.js` orders the two unchanged UMD modules and exports
  their API as native ES-module names. The browser uses the reference globals;
  Node uses its CommonJS namespace. Validation algorithms and errors are unchanged.
- `js/assignment-loader.js` adapts the generation counter, abort handling,
  manifest allowlist, no-store/no-redirect fetch, diagnostic wording and
  validate-before-commit pattern from `student/js/assignment-loader.js`. It removes
  maze DOM/reset callbacks, resolves files relative to its module's hosting path
  and leaves the active city/session alone on failures. Refresh invalidates old
  requests and clears the old allowlist; it does not clear the active assignment.
- `tests/test_assignment_contract.py` adapts the pure validation, schema and
  parity tests from `tests/test_assignment_data.py` and `tests/test_assignment_v2.py`.
  `tests/assignment_parity.mjs` drives the native adapter instead of the source's
  CommonJS test runner. All 364 shared validation cases and 76 answer selections
  are exercised without copying editor or maze tests.

City-specific session, selector and terminal adaptation remain separate from the
reference contract. No maze engine/UI, renderer, player physics, reset policy,
teacher GUI, private drafts or actual coursework is imported.
