# Three.js startup repair and self-hosted r187 — v1.0.1 review

Updated 2026-11-06 (Asia/Taipei), PR #6, branch `fix/pin-threejs-r187`.
**Status: instructor startup acceptance received for reviewed commit
`8d050156c66a121204dd5e605c8361058fb0a850`; merge and v1.0.1 publication authorized
after final CI verification. Nothing has been deployed to Apache.**

## Instructor acceptance — 2026-11-06

The instructor reports **Windows 11 Google Chrome: PASS** and **Windows 11
Microsoft Edge: PASS**. The original `StorageStructNode` startup failure is
resolved and the self-hosted Three.js 0.187.0 website loads successfully.
These are instructor-reported physical startup results, separate from the
automated coverage below. Browser versions, GPU/driver details, FPS and individual
detailed manual-check results were not supplied and are not inferred.

The instructor's earlier local packaging issue was resolved by downloading a
clean PR #6 source archive with an empty public assignment manifest, permitting
the 66-file package. It was not reported as a code defect; no runtime change is
made for that local packaging issue. This finalization changes documentation only.

## Confirmed incident and final architecture

The original unchanged v1.0.0 at `38b1dfdd73d766ec1d01999216b24dfca2126fad`
was reproduced in Chromium with:

`The requested module './three.tsl.js' does not provide an export named 'StorageStructNode'`.

The fetched WebGPU build referenced that symbol but the fetched TSL build did
not contain it. The original loading text remained and no renderer canvas was
created: the graph could not link, before `main.js` could evaluate or call
`initApp()`. Separate fetches of the floating `@dev` URLs returned different
bytes. The precise upstream/CDN cache history remains unverified. No original
working Three.js commit SHA was recorded in v1.0.0.

The first PR #6 commit (`f638558`) pinned all aliases to npm r187 on a CDN and
proved compatibility. That CDN map is now an intermediate historical step.
**The final candidate serves all Three.js code locally**, including its entire
recursive addon graph, from `vendor/three/0.187.0/`. Both `three` aliases resolve
to one WebGPU module URL, TSL/core share that installation, and addon relative
imports retain their original directory relationships. The obsolete jsDelivr
preconnect is removed. The static website needs no Node/npm or build framework
on Apache. Fonts have system fallbacks; YouTube/Forms remain external services,
so this is not a claim of a complete offline course product.

The existing small inline startup observer is retained unchanged. While the
loading overlay is active it handles script/graph errors and unhandled init
rejections, stops the indeterminate bar and gives a readable dependency/WebGPU
message. It does not suppress console errors or reopen the overlay after startup.
The missing-local-TSL test now exercises the actual application graph and a 404,
not just a synthetic module failure. No timeout/retry/device-loss redesign is added.

## Official distribution and exact vendor inventory

- Package: **three@0.187.0**, official metadata:
  <https://registry.npmjs.org/three/0.187.0>.
- Original tarball: <https://registry.npmjs.org/three/-/three-0.187.0.tgz>.
- Tarball size: **4,795,351 bytes**.
- SHA-512 npm integrity:
  `sha512-Qiu7R+Cmh8CstZsY1uJOSWnVlfo7ZtNLV7mF8Jltk3LB3AtDu9cRZlcnRKkAk8Y4z6KKw35z7Y7Urd7jWY8etA==`.
- Tarball SHA-256:
  `ff540832ded0cfe919764d24a3d88f3e2a05f23303f876423e4f893841e90728`.
- Verified normal TLS download, registry integrity and SHA-256 before reading
  tar members. No npm lifecycle/install scripts or tar filesystem extraction.
- [manifest.json](../vendor/three/0.187.0/manifest.json) is the exact path/size/
  SHA-256 inventory and provenance for **18 unchanged upstream files**: 17 JS
  modules plus the official [MIT LICENSE](../vendor/three/0.187.0/LICENSE).
  The manifest itself is the nineteenth distributed vendor file.
- All 18 upstream files were compared directly with official tar members.
  Re-running the vendor tool into an isolated checkout reproduced all 19 files
  byte-for-byte. No minification, patches, reformatting or substitutions.
  `.gitattributes` disables vendor text/EOL conversion on Windows; generated
  provenance always uses LF so its checksums remain reproducible there too.
  A Git checkout with `core.autocrlf=true` was verified to retain all 19 vendor
  files byte-for-byte. Original upstream whitespace is retained as well;
  owned-source whitespace checks exclude the immutable third-party files.

The 17 modules are:

```text
build/three.core.js
build/three.tsl.js
build/three.webgpu.js
examples/jsm/lighting/ClusteredLighting.js
examples/jsm/lights/SunLight.js
examples/jsm/lights/SunLightNode.js
examples/jsm/lights/SunLightShadow.js
examples/jsm/lights/SunShadowNode.js
examples/jsm/objects/SkyMesh.js
examples/jsm/tsl/display/BloomNode.js
examples/jsm/tsl/display/ImportanceSampledEnvironment.js
examples/jsm/tsl/display/SSRNode.js
examples/jsm/tsl/display/boxBlur.js
examples/jsm/tsl/lighting/ClusteredLightsNode.js
examples/jsm/tsl/utils/RNoise.js
examples/jsm/tsl/utils/SpecularHelpers.js
examples/jsm/utils/BufferGeometryUtils.js
```

The closure is found from the app's Three.js imports through upstream static
imports/reexports and literal dynamic imports. This r187 closure has no dynamic
imports or literal additional file assets. The tooling rejects unsupported/
computed dynamic imports, unmapped/external JS, missing inputs, inconsistent
maps, unsafe paths, source symlinks, provenance changes and checksum mismatches.
The manifest JS inventory must equal the graph, rather than silently packaging
unrelated examples. Vendor `../` relationships are permitted only after path
normalization stays inside this exact version directory; the existing first-party
no-traversal rule remains. The scanner targets the native syntax of this reviewed
snapshot, not arbitrary future JS: syntax/asset changes require review and the
independent real-browser graph check.

## Package, ZIP and integrity

The distribution is **66 files / 6,706,319 uncompressed content bytes**: the
original 47-file runtime shape plus 19 vendor files. Existing city/education JS,
CSS, geometry, schemas, assignment rules and source course data remain unchanged.
The public manifest is empty; real assignments, teacher files, tests, tools,
schemas, Git, caches and unrelated vendor examples are excluded. Full notices,
original headers and the MIT/OSM/NYC obligations are retained.

The tool follows the graph and verifies vendor checksums before creating output.
`--zip` additionally creates sorted members with fixed timestamps/permissions and
writes `SHA256SUMS.txt` from the completed archive. Two builds were compared
byte-for-byte and every ZIP member was checked against source. Compressor version
changes may change compressed bytes; final release metadata must always come
from the actual final ZIP, not an older candidate's hash.

Current **review artifact**, not a published release:

- Name: `engineering-city-lab-v1.0.1-web.zip`.
- ZIP size: **1,668,631 bytes**.
- SHA-256: `55a19e899fb207971f8c742d03640e801c9cc45e9be09bdec75f83ee0d36008c`.
- Artifacts: `/workspace/artifacts/engineering-city-lab-v1.0.1-review/`.
- The real ZIP was CRC-checked, its exact 66-member inventory checked, then
  extracted to `/tmp/city-vendor-extracted/` for the browser tests below.

## Automated checks and limitations

At this update's start, GitHub confirmed PR #6 remained Draft/open at `f638558`,
its CI had passed, and `main`/current stable v1.0.0 remained `38b1dfd`. Before
changes **190/190 Node** and **11/11 Python** tests passed.

After changes **190/190 Node** and **18/18 Python** tests pass. The original
364 validation cases and 76 answer selections are unchanged. Seven additional
Python tests exercise vendor checksums/missing modules/symlinks, version maps,
external/computed imports, graph escape, inventory/license/provenance and tarball
integrity; reproducible ZIP checks extend the existing package test.

Browser results use Chromium 154.0.8037.57:

- Native-DOM learning: three groups, three explicit intercepted provider actions,
  no page errors.
- Static package: three groups under a physical Apache tilde-prefixed path,
  including redirects/direct navigation/refresh, attribution and licenses.
- Startup diagnostics: five cases including an actual missing local TSL module,
  synthetic missing export, failed entry, rejected initialization and no overlay
  reactivation after success. Intentional errors are expected evidence.
- Native local-module/cache test: root, `course/city/` and
  `~username/engineering-city-lab/`; all 17 original modules evaluate as r187,
  both aliases share one instance, two ordinary reloads per path, **102 cache
  hits and 6 HTTP 304 responses**, zero page errors and no external requests.
  This suite uses no request routing and does not disable browser cache.
- Full packaged-city WebGPU: **24/24 groups passed**, with all four transport
  modes, 11 cameras, four light presets, map/search/teleport/Return, five fixed
  terminals, Demo, v1/v2 four/five-question units, retry/review, explanations/Form
  gates and safe replacement. All **57 script responses** (40 app + 17 Three.js)
  were local HTTP 200 with JavaScript MIME; **zero external or failed script
  requests**, page errors or GPU device loss. The sole resource console error
  was the deliberately injected assignment HTTP 503. Startup and night images
  were inspected; screenshots and network evidence are retained outside Git.

The full-city test blocks every external HTTPS host, including jsDelivr and
other external Three.js hosts; it does not fulfill or cache any CDN bytes. It
checks every script's local URL/MIME/status, the exact 17-file vendor inventory,
and zero external/failed script requests. Synthetic provider document routes
are registered separately before explicit video/Form actions. Fonts are blocked
and existing system fallbacks are used. No real video playback/Form submission,
university Apache access or hardware-GPU performance is inferred.

Full-city rendering uses software Vulkan/SwiftShader and test-only observability/
deterministic stepping of the actual production loop. This is compatibility
coverage, not Windows hardware-GPU acceptance or an FPS benchmark.

Reproduce from the reviewed checkout (choose new artifact paths):

```sh
node --test --test-reporter=tap tests/*.test.cjs tests/*.test.mjs
python3 -m unittest tests.test_assignment_contract tests.test_release -v
python3 tools/check_release.py --syntax
python3 tools/check_release.py
python3 tools/package_release.py --output /tmp/city-review-site --zip /tmp/engineering-city-lab-v1.0.1-web.zip
python3 tests/browser_startup.py --site-root /tmp/city-review-site --output /tmp/city-review-startup
python3 tests/browser_vendor.py --site-root /tmp/city-review-site --output /tmp/city-review-cache
python3 tests/browser_learning_dom.py --output /tmp/city-review-dom
python3 tests/browser_release.py --site-root /tmp/city-review-site --output /tmp/city-review-static
python3 tests/browser_education.py --workflow --base-path course/city/ --site-root /tmp/city-review-site --output /tmp/city-review-browser
```

For artifact testing, extract the verified ZIP and pass the extracted directory
to `--site-root`. Current evidence: `/tmp/city-vendor-*.log`,
`/tmp/city-vendor-node.tap`, `/tmp/city-vendor-browser/results.json` and
`network.json`, screenshots, `/tmp/city-vendor-cache/results.json` and the other
browser evidence directories. Existing read-only PR CI includes all Python
release tests, Node tests and vendor syntax/integrity checks; full WebGPU tests
remain separately executed.

## Exact source inventory for this update

The 19 added versioned vendor files are listed individually above and in the
manifest (17 modules, LICENSE, manifest). Other changes are:

- `index.html`: local import map; obsolete CDN preconnect removed; diagnostics retained.
- New `.gitattributes`: retain exact vendor bytes on Windows Git checkouts.
- `README.md`, `THIRD_PARTY_NOTICES.html`: current local runtime and license links.
- `tools/package_release.py`: import-map graph, vendor integrity and deterministic ZIP/checksum.
- `tools/check_release.py`: include vendored JS in syntax checks.
- New `tools/three_runtime.py`, `tools/vendor_three.py`: pinned provenance, graph rules and offline reproduction from the official tarball.
- `tests/boot.test.cjs`, `tests/test_release.py`: local aliases, nested URLs, vendor/package/ZIP regressions.
- `tests/browser_education.py`, `tests/browser_startup.py`: no-CDN full-city network evidence, map search and actual missing-local-dependency failure.
- New `tests/browser_vendor.py`: ordinary module refresh/cache at three physical paths.
- `docs/deployment.md`, `docs/upstream.md`, `docs/release-checklist.md`, this report and new `docs/v1.0.1-release-notes.md`: deployment, upgrade, acceptance and release preparation.

No production file under `js/`, `css/`, `schemas/` or `assignments/` is changed.
No unrelated library, teacher GUI, framework, backend or tracking is introduced.

## Get and test the candidate on Windows 11

The downloadable review ZIP and SHA256SUMS accompany this conversation. The
branch source ZIP is also available through GitHub **Code → Download ZIP** at:
<https://github.com/chingchechung/engineering-city-lab/tree/fix/pin-threejs-r187>.
That GitHub source archive is not the deployable website ZIP. Alternatively:

```powershell
git clone --branch fix/pin-threejs-r187 https://github.com/chingchechung/engineering-city-lab.git engineering-city-lab-v1.0.1-review
cd engineering-city-lab-v1.0.1-review
git rev-parse HEAD
New-Item -ItemType Directory -Path C:\Temp\city-v1.0.1-review
py -3 tools\package_release.py --output C:\Temp\city-v1.0.1-review\site --zip C:\Temp\city-v1.0.1-review\engineering-city-lab-v1.0.1-web.zip
Get-FileHash C:\Temp\city-v1.0.1-review\engineering-city-lab-v1.0.1-web.zip -Algorithm SHA256
Get-Content C:\Temp\city-v1.0.1-review\SHA256SUMS.txt
py -3 -m http.server 8000 --bind 127.0.0.1 --directory C:\Temp\city-v1.0.1-review\site
```

Repeat in Chrome and Edge, record versions/GPU/driver and pass/fail:

1. Open localhost, reload with and without cache, confirm the city loads and no
   missing module/export, shader or device-loss error. Block `cdn.jsdelivr.net`;
   confirm no remote script requests and all 17 Three.js files are local vendor URLs.
2. Walk, drive/brake, cycle, fly/ascend/descend; check traffic/collisions/audio,
   all 11 cameras and four light presets including night shadows/reflections.
3. Map/search/teleport/Return work; each fixed terminal remains reachable with X
   and the original proximity/speed rules. Demo retry preserves passes and dialogs
   pause/restore controls cleanly.
4. Use the existing v1 and v2 fixture reviewer for four/five questions, Q05 rules,
   single-label acceptance, explanations/Form gates and failed/cancelled replacement.
   `--review-browser chrome`/`msedge` intentionally mocks provider tabs.
5. Block one local `three.tsl.js` request and reload: readable startup failure;
   unblock/reload: normal recovery. Test the actual approved HTTPS nested host
   separately before any production deployment.

## Future Three.js upgrades

Use a separate reviewed change. Obtain the chosen exact version's registry
metadata/tarball over verified TLS; record/verify official integrity and SHA-256.
Update provenance/version constants, then run `tools/vendor_three.py --tarball`
against a new version directory. It never fetches, executes npm scripts or modifies
upstream bytes. Review the discovered closure, any new syntax/assets and license;
update all four aliases together. Keep version directories immutable, regenerate
checksums/inventory and package expectations, run complete CI/packaged-city tests
with external scripts blocked, ordinary-cache tests and physical Windows review.
Do not silently upgrade, flatten paths or overwrite an old version with new bytes.

## Release and deployment gates

Instructor startup acceptance and publication authorization were received on
2026-11-06 as recorded above. Verify successful CI for the final documentation
head, mark PR #6 ready, merge
PR #6, verify exact merged `main`, annotate/tag **v1.0.1** at that commit, regenerate
and verify the clean ZIP/checksum from it, then publish the separately prepared
release notes/assets. Recompute metadata from the actual uploaded ZIP and compare
its downloaded digest/checksum; never copy v1.0.0 or an older review ZIP hash.
If API/upload access fails, provide verified files and notes for manual upload and
do not claim publication. Preserve v1.0.0 tag and assets unchanged.

No university Apache deployment is part of this task. For any later authorized
deployment, stage a complete version directory, back up existing site/course data
privately, retain notices, verify HTTPS/nested paths/MIME/404/local vendor loading,
then switch the entry point. Keep coursework publication separate (unit first,
manifest last). Roll back to a complete instructor-verified site/dependency
snapshot; original v1.0.0's floating CDN HTML can reproduce this incident and is
not an assured working dependency rollback. Source rollback uses a normal revert
on a review branch, never history/tag rewriting.
