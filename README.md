# Engineering City Lab

Digital Electronics practice in the original [Slop New York](https://github.com/mrdoob/slop-newyork/) city by Mr.doob, built with [Three.js](https://threejs.org/), WebGPURenderer and TSL. Walk, drive, cycle or fly; the complete city, maps and teleports remain available.

Serve this directory over HTTP for local development:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/` in a WebGPU-capable Chrome/Edge browser. Production needs **HTTPS**, or a secure browser context; arbitrary plain HTTP university hosts may disable WebGPU. No server Node runtime, database or application build is needed. Internet access to the existing CDN dependencies is required; opening `index.html` as `file://` is unsupported.

Approach a fixed terminal and press **X** while stationary. Wrong answers can be retried. For published assignments, open the question video on request, choose one answer, optionally review the explanation after passing, and open Google Forms at 4/4 or 5/5. No exit or map timer is required. The public manifest is empty by default; Demo Mode has synthetic local questions and no fabricated external links. Progress lasts until the page reloads.

The [upstream live demo](https://mrdoob.github.io/slop-newyork/) is the original city, without these assignments.

## Release and teaching

- [Static packaging, Apache installation and regression commands](docs/deployment.md)
- [Teacher GUI export and manual publication](docs/teacher-publishing.md)
- [Release checklist and final Windows checks](docs/release-checklist.md)
- [Phase 4 evidence, exact changes and limitations](docs/phase-4-results.md)
- [Architecture](docs/architecture.md), [development rules](AGENTS.md) and [phased plan](Plan.md)

JSON and its correct answers are public: this is practice software, not a secure examination system. No login, telemetry or student database is added. Google Forms handles submissions independently.

## License and data

Original Slop New York source is available under the [MIT License](LICENSE), Copyright (c) 2026 Mr.doob. Reused assignment components retain their separately documented instructor authorization and [provenance](docs/assignment-reuse.md); no blanket license for the reference project is inferred.

Geographic data: NYC Open Data and © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright) (ODbL). Third-party data and dependencies retain their respective licenses.
Retain the distributed [licenses and data notices](THIRD_PARTY_NOTICES.html), including the Three.js notice for ported geometry code. The [upstream audit](docs/upstream.md) records import identity, dataset terms and the unchanged floating `@dev` dependency risk.
