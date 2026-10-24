# Imported upstream, dependencies and licensing

Recorded 2026-10-23 (Asia/Taipei) during Phase 0. No upstream or dependency update
was performed.

## Exact import identity

| Property | Verified value |
| --- | --- |
| Educational repository | [chingchechung/engineering-city-lab](https://github.com/chingchechung/engineering-city-lab) |
| Imported baseline on `main` | `cca9c12a096951d63fee1d26904c04be0a128cef` — Import Slop New York |
| Baseline tree | `87dd55d636bb6a577e5aa4aa79a6bfc93890aae6` |
| Upstream repository | [mrdoob/slop-newyork](https://github.com/mrdoob/slop-newyork) |
| Imported upstream commit | [`4b899b006120155514aee2e1558b4d14906c87e4`](https://github.com/mrdoob/slop-newyork/commit/4b899b006120155514aee2e1558b4d14906c87e4) |
| Upstream commit subject | Refine bicycle drivetrain and rolling sounds |
| Upstream commit time | 2026-10-23 20:25:02 Asia/Taipei (12:25:02 UTC) |
| Upstream tree | `0cf48ecf769c979c9d7797403c7cc46d95ee2d9f` |

The import is a two-parent merge: first parent
`e5452fa60e41f3ddc5b9e90caeaec0ff9be8d137` preserves the project's initial
README; second parent is the upstream commit above. The upstream GitHub commit
record independently confirms that SHA and tree. The only tree difference
between upstream and the imported baseline is the added two-line
`README-initial.md`. All city source, UI, tests, tools and data match upstream.

Reproduce locally:

```sh
git show -s --format='%H %T %P' cca9c12a096951d63fee1d26904c04be0a128cef
git diff --name-status 4b899b006120155514aee2e1558b4d14906c87e4 cca9c12a096951d63fee1d26904c04be0a128cef
```

There is no imported release/version manifest. The commit is the city version;
do not describe a later upstream HEAD or a Three.js release number as this import.

## Dependency state to preserve

This is a static native-ES-module application, with no `package.json`, lockfile,
bundler, vendored Three.js build or install step. The import map in `index.html`
contains these exact dependency URLs:

| Specifier | URL |
| --- | --- |
| `three` | `https://cdn.jsdelivr.net/gh/mrdoob/three.js@dev/build/three.webgpu.js` |
| `three/webgpu` | `https://cdn.jsdelivr.net/gh/mrdoob/three.js@dev/build/three.webgpu.js` |
| `three/tsl` | `https://cdn.jsdelivr.net/gh/mrdoob/three.js@dev/build/three.tsl.js` |
| `three/addons/` | `https://cdn.jsdelivr.net/gh/mrdoob/three.js@dev/examples/jsm/` |

`@dev` is a moving branch, not an immutable dependency version. The repository
does not record the resolved Three.js SHA or CDN bytes used for the instructor's
successful Windows test. Source comments mention r186/r187 compatibility; those
comments do not establish a pinned version. Preserve the URLs during preparation
and the initial integration. A later reviewed pin should capture one compatible
snapshot for every alias/addon and rerun physical browser checks.

The runtime also requests Inter and Overpass through Google Fonts, from
`fonts.googleapis.com` and `fonts.gstatic.com`; system fallbacks are defined in
CSS. Geographic data and geometry are local. There are no runtime question
fetches in the import. The city requires HTTP(S) hosting for native modules and
external dependency access; the existing source is not an offline bundle.

## Notices and redistribution

| Component | Existing record and requirement |
| --- | --- |
| Slop New York source | [LICENSE](../LICENSE): MIT, Copyright (c) 2026 Mr.doob. Preserve the complete copyright, permission and warranty notice in copies/substantial portions, including distributions. |
| Upstream credits | Keep [README.md](../README.md)'s MIT and geography attribution. New educational documentation supplements these notices. |
| Three.js and ported geometry | Three.js is MIT; `actor-models.js` identifies a port of `LoftGeometry`. Preserve upstream notices and include the applicable Three.js license if a later release vendors/bundles that dependency. [Three.js license](https://github.com/mrdoob/three.js/blob/dev/LICENSE). |
| OpenStreetMap geography | The README and generated data header credit © OpenStreetMap contributors and ODbL. Preserve source attribution and the [copyright/license link](https://www.openstreetmap.org/copyright). Distribution of adapted databases must follow applicable ODbL attribution, share-alike and access obligations; the code's MIT license does not replace them. |
| NYC Open Data | `geo-base.mjs` identifies DCP Borough Boundaries (`gthc-hcne`), Street Centerline/CSCL (`inkn-q76z`) and Parks Properties (`enfh-gkve`). Preserve source credits and consult dataset-specific terms before republishing/replacing data. [NYC Open Data terms](https://opendata.cityofnewyork.us/overview/#termsofuse). |
| Fonts | Inter and Overpass are external font dependencies with their own licenses. Retain their applicable font notices if vendoring fonts later; do not label third-party font files as project MIT code. |
| Reference assignment project | Inspected at `70cc35d9ce828bcd5357f16fe85f303aa2d30cd9`; no root-level LICENSE was found. `showcase3d/dist/LICENSES.txt` is a bundled-dependency notice, not a blanket license for the application. The instructor explicitly authorizes reuse of their reference assignment components in Phase 2. Preserve source headers and provenance; this permission does not assign a new blanket license to the reference project or copy bundled third-party code. See [assignment reuse](assignment-reuse.md). |

The imported UI linked the upstream repository but lacked a dedicated OSM
attribution. Phase 4 adds a small visible credit linking OSM's copyright page,
plus a local [licenses and data notice](../THIRD_PARTY_NOTICES.html). It remains
visible in the city, full map and clean view. The renderer and city HUD systems
are unchanged; this is the separately authorized distribution attribution.

## Data provenance and tooling

`js/nyc-geodata.js` is generated by `tools/build-geodata.mjs`, using the seven
checked-in source JSON files and four `.overpassql` query files in `tools/data/`.
The generated header records the world frame and NYC/OSM sources. The builder
uses local inputs; it does not need live data downloads. `tools/overpass.sh` is
the separate download utility and validates a temporary response before atomic
replacement. Do not refresh those datasets for an educational feature.

`geo-base.mjs` mentions `tools/fetch-geodata.sh`, but that script is not in the
imported tree. The generator can run from the checked-in inputs; a complete
automated refetch pipeline is not present. No new one was added in Phase 0.

## Phase 4 release audit

Reviewed 2026-10-24 (Asia/Taipei). The package retains the full Mr.doob MIT
`LICENSE`, every original module/source header, and `THIRD_PARTY_NOTICES.html`.
The latter includes the full Three.js MIT notice for already ported LoftGeometry/
CarGenerator code, even though the renderer itself remains CDN-hosted. Inter and
Overpass are external, with Google Fonts OFL source links; no font files are
distributed. Assignment runtime components retain the instructor's reuse
authorization and exact pinned provenance, without inferring a reference-wide
MIT license. Test-only fixtures and authoring tools are excluded.

The [OSMF attribution guidelines](https://osmfoundation.org/wiki/Licence/Attribution_Guidelines)
and [OSM copyright page](https://www.openstreetmap.org/copyright) require credit
and access to licensing information. A repository-only README was insufficient
for ordinary users of the distributed simulation. The added visible strip
provides that access without changing map/city mechanics. The local notice names
the [ODbL 1.0 terms](https://opendatacommons.org/licenses/odbl/1-0/) and provides a
relative link to the **entire distributed machine-readable geographic database**,
`js/nyc-geodata.js`, plus the exact source inputs/generator revision. OSM-derived
database rights remain under ODbL; MIT covers neither all data nor NYC's rights.
Keep those links/notices and free data access in every installation. New data
adaptations need their own ODbL share-alike/access review.

The old NYC overview terms anchor now redirects to a general information page.
Use the actual [NYC Open Data terms](https://data.cityofnewyork.us/stories/s/Terms-of-Use/k9k7-3cje)
and [official public policies](https://cityofnewyork.github.io/opendatatsm/publicpolicies.html).
The notice identifies all three source IDs, the imported source revision,
modifications/projection and lack of City warranty/endorsement. Live source pages
can change; the imported tree does not establish original retrieval dates or
an individual blanket data license. A university distributor should confirm any
additional dataset/entity terms before public distribution, retaining this source
identification rather than claiming all assets are MIT. No geographic inputs or
generated bytes were changed or refreshed during this audit.

**Separately reviewable dependency recommendation:** retain the current import
map in this phase. In a later instructor-approved dependency-only PR, identify a
single immutable Three.js Git SHA compatible with the accepted city; point **all
four aliases and the addons prefix** at that same SHA on the same CDN. Capture
the exact resolved URLs and hashes, rerun all regressions, then compare physical
Windows Chrome/Edge rendering, shaders, all cameras/modes and map behavior before
approval. Keep a one-commit rollback and avoid mixed snapshots. Do not infer the
tested SHA from `@dev`, source comments, an npm release number or a cache timestamp.
The earlier accepted browser snapshot has no recorded upstream Three.js SHA.
Pinning is not performed, and floating CDN bytes remain a reproducibility and
future-availability limitation of this release candidate.
