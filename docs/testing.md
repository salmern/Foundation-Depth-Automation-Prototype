# Current testing status

## Executed

- **70 Python tests discovered: 59 passed, 11 dependency-based integration tests skipped.** Log: outputs/offline-test-results.txt.
- Independent brief example gives **97.950 / Pipe**. Decimal validation, missing/invalid values, fallback restrictions, negative clear-distance clamp, tie priority and rounding are covered.
- Coordinate fitting/holdout/rejection, ambiguity-preserving point matching, archive safety, persistence, interrupted/failed jobs and real report creation are covered.
- The new bounded ASCII reader was run against **all nine actual supplied DXFs**, including the 450,784,383-byte main drainage drawing. Evidence: outputs/streamed-source-evidence.json and streamed-source-run.txt. No source file was modified.
- Actual marker visibility resolves 679 numbered candidates: 170 each for numbers 1,3,4; 169 for 2. This does not verify physical corners/plot associations.
- Additional tests cover invisible labels, ambiguous visible labels, excluded OLE payload, missing EOF, nonfinite geometry, joined MTEXT segments, INSERT attributes, independently expected draft cell mapping, blocked blank outputs, duplicate/unsupported results and audited immutable revisions.
- Python source/tests/scripts compile. Frontend TS/TSX parses with the system Babel parser (syntax only). Bash launch helpers pass bash -n (syntax only).
- Initial source inspection workbook passes ZIP/CRC/XML checks and preserves original worksheet/style parts byte-for-byte. It has not been opened by openpyxl/Excel here.

## Not executed

Registries remain unreachable (DNS failure), so dependencies are absent. **FastAPI startup, Next build/full type checking, ezdxf/openpyxl/Shapely runtime, Vitest, Playwright and helper service startup are not claimed passing.** Installation attempts are recorded in outputs. There is no fabricated lockfile or substituted hardcoded-success backend.

Eleven real-library/API integration tests are written for CAD handles, invalid polygons, schema validation, actual workbook mapping, changed-template rejection, populated draft/reopen verification, API creation/uploads/results/download, draft registration, audited revisions and failed jobs.

Vitest/Testing Library tests cover API schema/network/error boundaries, project creation/empty/error states, upload rejection, calculation dialog, issue filters and output download. The browser test uses the real backend, real uploads, explicitly synthetic reviewed inputs and the **actual master template**; it downloads a populated draft and checks U10=97.95 with openpyxl. No final construction schedule is asserted complete.

The step-by-step commands and launch prerequisites are in [LOCAL_SETUP_AND_WORKFLOW.md](../LOCAL_SETUP_AND_WORKFLOW.md).

## Reproduce after installing dependencies

From foundation-mvp:

```sh
.venv/bin/python -m pytest backend/tests -v
cd frontend
npm run typecheck
npm run build
npm test
npx playwright install chromium
npm run test:e2e
```

Stop existing servers for isolated E2E runs. The test expects .venv/bin/python and the supplied parent 2 Template/MASTER Foundation Schedule.xlsx. E2E data uses data/e2e. Windows needs the documented Python executable path adaptation.

Without downloaded libraries:

```sh
python3 -m unittest discover -s backend/tests -v
python3 -m compileall -q backend/src scripts
python3 scripts/process_source_evidence.py
bash -n scripts/setup.sh scripts/run-backend.sh scripts/run-frontend.sh scripts/start-local.sh
```

## Independent expected results and limitations

No complete trusted site answer schedule was supplied. Synthetic inputs/expected values are specified independently rather than generated from the application's output. The brief verifies the arithmetic example, not all client plot corners, tree/geology rules, physical associations or complete workbook dependencies. A draft schedule and the generated source evidence report are not engineering golden truth. No Docker or production deployment was tested.
