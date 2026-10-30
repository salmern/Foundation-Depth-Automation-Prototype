# Foundation Depth Automation

Local FastAPI + Next.js application for DXF evidence inspection, engineering review, deterministic corner calculations and draft output in the client's existing Excel template.

**Start here: [Local setup and complete workflow guide](LOCAL_SETUP_AND_WORKFLOW.md).**

For a public Render demo, see [Deploy to Render](DEPLOY_TO_RENDER.md). The demo configuration uses free services and temporary storage.

The setup guide includes Ubuntu/Linux and Windows commands, launch helpers, a first test run, real-file processing, corrections, outputs, storage, tests and troubleshooting.

Additional detailed handover documents:

- [Build walkthrough: architecture, code structure, backend, frontend, calculations and delivery](BUILD_WALKTHROUGH.md)
- [Video demo presentation script: narration, screen actions, code tour and recording alternatives](VIDEO_DEMO_PRESENTATION_SCRIPT.md)

## Current delivery

- Persistent local projects, validated immutable uploads, background jobs and real frontend/API communication.
- ezdxf inspection plus a bounded ASCII DXF reader for large files. All nine supplied DXFs, including the 450 MB drainage file, were parsed locally.
- Actual visibility-aware extraction of 679 numbered marker candidates: 170 each for 1, 3 and 4; 169 for 2. These are not automatically verified physical house corners.
- Coordinate-fit validation, explicit reviewed inputs, source-handle checks and deterministic Decimal calculations.
- Audited reviewed-input revisions in the frontend; original/revised source bytes, hashes, reviewer, reason and time retained.
- Review-only workbooks when inputs are incomplete; populated **draft schedules** in confirmed template output columns when reviewed corner results exist. Original uploads and unrelated formulas/styles are preserved; missing outputs stay blank.
- Source inventories, engineering documentation, real-backend API/browser test source and launch scripts.

## Verification

**59 tests passed; 11 library/API tests skipped.** The independent brief example produces **97.950 m / Pipe**. Python compilation, frontend TS/TSX syntax and Bash helper syntax checks pass. Actual source-reader evidence is in [streamed-source-evidence.json](outputs/streamed-source-evidence.json).

Registry DNS is unavailable in this execution environment. FastAPI/Next startup, full TypeScript build, openpyxl runtime export, Vitest and Playwright remain unverified here. See [testing status](docs/testing.md); skipped tests are not counted as passing. The setup guide explains how to install/run them locally.

A **final construction schedule from these client drawings remains blocked** by engineering/source gaps: coordinate alignment, physical plot/corner association, survey/service associations, missing tree/planting inputs and unconfirmed workbook branches. The application exposes those gaps rather than guessing. Draft schedule support does not remove that requirement.

## Quick local commands

Inside foundation-mvp, on a Linux machine with Python 3.11+, venv support, compatible Node/npm and installation internet access:

```bash
bash scripts/setup.sh
bash scripts/start-local.sh
```

Open http://127.0.0.1:3000. Press Ctrl+C to stop the combined launcher. Read the guide before using client results; helper service startup is not claimed tested in the restricted development environment.

## Key files

- [Step-by-step setup and beginning-to-end explanation](LOCAL_SETUP_AND_WORKFLOW.md)
- [Requirements and remaining engineering questions](docs/requirements.md)
- [Calculation specification and output mapping](docs/calculation_specification.md)
- [Data dictionary and reviewed-input schema](docs/data_dictionary.md)
- [API](docs/api.md), [coordinate investigation](docs/coordinate_mapping.md), [limitations](docs/limitations.md)
- [Test results](outputs/offline-test-results.txt)
- [Original-source preservation check](outputs/original-preservation-check.json)
- [Initial inspection report](outputs/source-validation-report.json) and [inspection-only workbook](outputs/source-inspection-review-only.xlsx). These are initial source-audit artifacts, not generated client schedules. Later visibility/large-file findings supersede the original runtime-limit findings; see streamed-source-evidence.json.

No API keys, AI agent SDK, cloud service, database or authentication provider is required for the local core. Original source files were preserved.
