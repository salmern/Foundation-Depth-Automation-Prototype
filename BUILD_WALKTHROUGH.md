# Foundation Depth Automation — complete build walkthrough

This document explains the implementation from source inspection to the frontend, backend, calculations, outputs, testing and handover. It describes the code that exists, rather than treating all originally requested functionality as complete.

For installation and operating commands, use [LOCAL_SETUP_AND_WORKFLOW.md](LOCAL_SETUP_AND_WORKFLOW.md). For a narrated presentation, use [VIDEO_DEMO_PRESENTATION_SCRIPT.md](VIDEO_DEMO_PRESENTATION_SCRIPT.md).

## 1. Executive explanation

The client's manual task is to determine a foundation bearing elevation at each of four corners of a house. Engineers gather levels and constraints from several drawings, compare candidate bearing elevations and enter the controlling result into the client's Excel schedule.

The application implements a local evidence-review and conditional draft-schedule workflow:

1. Create a persistent project.
2. Upload source drawings, the actual Excel template and, when available, explicitly reviewed corner inputs.
3. Validate and preserve uploaded files.
4. Inspect DXF entities, layers, blocks, references and coordinates.
5. Extract raw evidence and visible numbered marker candidates.
6. Investigate alignment using explicit reference evidence.
7. Validate reviewed plot/corner/constraint decisions.
8. Calculate supported bearing-level candidates deterministically in Python.
9. Show source references, calculation explanations and unresolved issues.
10. Generate a review attachment or populate confirmed output columns as an explicitly labelled draft.
11. Retain source revisions, calculations, reports and audit records locally.

It is not currently an independently verified, fully automatic construction-schedule generator for the entire supplied site. That distinction is visible in the interface, output labels and documentation.

## 2. What was inspected before implementation

The existing workspace was inspected before application code was added. It contained the supplied engineering materials and a broken existing virtual environment, but no application/prototype code to preserve or replace.

|Material|Inspection and finding|
|---|---|
|Build brief PDF and DOCX|Read the text, including the independently issued drainage arithmetic example and required reason labels.|
|Foundation PDF|Extracted text locally with pdftotext; inspected service details, minimum-depth conditions, source references and vegetation notes. Production PDF geometry interpretation is not implemented.|
|MASTER Foundation Schedule.xlsx|Inspected the actual workbook's ZIP/XML structure, sheets, headers, formulas, named ranges and column metadata.|
|Original DWGs|Inventoried and preserved. Direct DWG parsing/conversion is not implemented.|
|dxf files.zip|Inspected nine converted drawings without extracting into original source directories.|
|Expanded drainage packages|Identified duplicated files using hashes; no arbitrary revision precedence was chosen.|
|Other assets and references|Recorded their filenames, formats, sizes, readability and source status.|

There were **78 supplied files** and **35 groups of byte-identical duplicate files**. The source inventory and original-preservation check record these findings. All original source hashes were checked as unchanged after implementation.

Important discoveries were:

- The main drainage DXF is **450,784,383 bytes**, with large OLE payloads.
- Foundation coordinates have a different magnitude from drainage/topographical coordinates; a scale hypothesis is not sufficient validation.
- Some drawing unit headers are unspecified or inconsistent with the observed coordinates.
- The layout has **106 unique plot-label texts**. This is a label count, not a verified count of complete houses.
- The corner drawing contains **679 numbered marker candidates**. Number visibility resolves from the blocks' entity flags, but physical house-corner and plot associations remain unverified.
- Referenced standalone tree/planting information was not found in the pack.
- The workbook includes `Vibro` and `Ask the Engineer` branches beyond the seven reason labels in the prose brief.
- The original workbook already contains cached formula errors and prompts; copying it does not resolve its engineering inputs.

Evidence files are in [docs/source_inventory.md](docs/source_inventory.md), [docs/workbook-inspection.json](docs/workbook-inspection.json), [outputs/streamed-source-evidence.json](outputs/streamed-source-evidence.json) and the other inspection artifacts under docs/outputs.

## 3. Scope and verification at handover

|Category|Actual position|
|---|---|
|Source implementation|Frontend, backend, local persistence, readers, reviewed revisions, calculation primitives and review/draft exporters are implemented.|
|Actual supplied drawings|All nine ASCII DXFs were exercised using the bounded reader.|
|Numbered markers|679 candidates resolved: 170 each for numbers 1, 3 and 4; 169 for number 2.|
|Verified physical client plot corners|Zero claimed. Marker candidates have not been independently matched to every physical corner and plot.|
|Python test run|70 tests discovered: **59 passed, 11 dependency-based integration tests skipped**.|
|Other executed checks|Python compilation, TypeScript/TSX syntax parsing and Bash helper syntax checks.|
|Full-stack execution|Not verified in the restricted development environment because dependency registries could not be resolved.|
|Client construction schedule|Not verified or issued as complete.|

The skipped tests are not passing tests. Syntax checks are not a Next.js build or browser test. The actual source-inspection attachment was checked at ZIP/XML/byte-preservation level, not opened with Excel/openpyxl in that environment.

## 4. System architecture

```text
Browser: Next.js / React / TypeScript
    |
    | HTTP requests through one API client; schema-checked responses
    v
FastAPI: validation, project and job endpoints, output downloads
    |
    | local single-worker processing job
    v
Processing pipeline
    +-- safe source inventory and working-copy preparation
    +-- ezdxf / bounded ASCII DXF inspection
    +-- coordinate evidence and controlled geometry primitives
    +-- reviewed plot/corner/constraint validation
    +-- deterministic Decimal engineering calculations
    +-- issue generation and schedule checks
    +-- template-based review/draft Excel output and verification
    |
    v
Local files: project JSON, immutable sources, run folders and reports
```

The separation has a practical purpose:

- The frontend manages interaction and display.
- The backend is authoritative for validation, calculation results and output availability.
- Engineering arithmetic is isolated from both HTTP handling and React.
- CAD inspection preserves raw evidence without automatically certifying its engineering meaning.
- Local persistence avoids a database/cloud dependency for this single-operator MVP.

No LLM, Claude Agent SDK, API key or cloud service participates in calculation or core processing. Installation needs package downloads; the installed core does not need an online AI service.

## 5. Repository structure

```text
foundation-mvp/
├── README.md
├── LOCAL_SETUP_AND_WORKFLOW.md
├── BUILD_WALKTHROUGH.md
├── VIDEO_DEMO_PRESENTATION_SCRIPT.md
├── .env.example
├── .gitignore
├── backend/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── src/foundation_mvp/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── storage.py
│   │   ├── safety.py
│   │   ├── pipeline.py
│   │   ├── cad.py
│   │   ├── streaming.py
│   │   ├── geometry.py
│   │   ├── engineering.py
│   │   ├── review.py
│   │   └── excel.py
│   └── tests/
│       ├── test_core.py
│       ├── test_completion.py
│       ├── test_integration.py
│       └── fixtures/
│           ├── synthetic-house.dxf
│           └── synthetic-reviewed-inputs.json
├── frontend/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   ├── globals.css
│   │   └── projects/[id]/page.tsx
│   ├── components/
│   │   ├── workspace.tsx
│   │   ├── review-editor.tsx
│   │   └── ui/{button,dialog}.tsx
│   ├── lib/{api,schemas,utils}.ts
│   ├── tests/
│   │   ├── api.test.ts
│   │   ├── dashboard.test.tsx
│   │   ├── workspace.test.tsx
│   │   ├── review-editor.test.tsx
│   │   ├── setup.ts
│   │   └── e2e/workflow.spec.ts
│   ├── package.json
│   ├── next.config.mjs
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.mjs
│   ├── vitest.config.ts
│   ├── playwright.config.ts
│   └── .env.example
├── scripts/
│   ├── setup.sh
│   ├── start-local.sh
│   ├── run-backend.sh
│   ├── run-frontend.sh
│   ├── check_environment.py
│   ├── inspect_sources.py
│   ├── process_source_evidence.py
│   ├── create_fixture.py
│   └── create_source_review.py
├── docs/
├── outputs/
└── data/working/       # created as projects are used; not committed runtime data
```

The project is deliberately divided into a small number of functional modules rather than empty folders for every possible feature.

## 6. Technology choices and their exact roles

|Technology|Role in this repository|
|---|---|
|Next.js App Router|Application shell and project routes.|
|React and TypeScript|Interactive dashboard, workspace, form state and typed component code.|
|Tailwind CSS|Responsive layout, consistent spacing, typography and status styling.|
|Radix UI and shadcn-style components|Button composition and accessible modal dialog behavior. This is a small local component set, not a claim that a complete shadcn library was generated.|
|Zod|Runtime validation of successful API responses in the frontend.|
|FastAPI and Uvicorn|HTTP API, generated OpenAPI documentation and local server.|
|Pydantic|Request/response models, finite engineering values and reviewed-input structure.|
|ezdxf|Inspection of normal-sized supported DXF documents.|
|Bounded standard-library reader|ASCII DXF inspection for large files while not retaining opaque OLE payload.|
|Shapely|A polygon validity/corner helper. It is not yet a complete automatic site-outline matching system.|
|Python Decimal|Deterministic arithmetic and final rounding.|
|openpyxl|Runtime inspection and template-based review/draft export. Source exists; execution remained unverified here.|
|unittest / pytest|Backend primitive, lifecycle, source and integration test coverage.|
|Vitest / React Testing Library|Frontend component and client-boundary test source.|
|Playwright|Real-backend browser workflow test source.|

The frontend currently uses React form state and HTML form validation; React Hook Form was not added simply because it appeared as an optional suggestion in the brief.

## 7. Backend walkthrough, module by module

### 7.1 main.py — HTTP application boundary

[backend/src/foundation_mvp/main.py](backend/src/foundation_mvp/main.py) creates the FastAPI app and configures:

- Local-development CORS origins.
- Structured HTTP, request-validation and unexpected-error responses.
- Project creation/list/retrieval.
- Multipart file uploads and input deactivation.
- Processing start and job-status retrieval.
- Extraction, coordinates, plots, calculations and issue retrieval.
- Reviewed-input read/revision endpoints.
- Draft output registration retrieval and file downloads.
- A clearly labelled source-brief arithmetic example endpoint.

A lifespan handler marks abandoned running jobs interrupted and creates a single processing executor. On shutdown, the executor is closed. A running job blocks conflicting mutations and duplicate processing requests.

The API does not execute uploaded files or follow uploaded xref paths. File downloads use registered output IDs and check that the resolved file remains inside the project directory and exists.

### 7.2 models.py — explicit contracts

[models.py](backend/src/foundation_mvp/models.py) defines project creation, source references, constraints, corners, plots, reference points, alignments, reviewed documents, revisions and response views.

Important validation rules include:

- Printable project names and bounded lengths.
- Finite engineering numbers; booleans are not accepted as numeric measurements.
- Corner identifiers are integers 1–4.
- Exactly one occurrence of each corner within a reviewed plot.
- Exactly one applicability decision for each of the seven supported constraint reasons.
- No unexpected fields in strict request/input models.
- Distinct drawing pairs for reviewed alignments.
- Required revision reason and explicit reviewer/review rationale.

Input validation establishes structural correctness. It does not prove that a reviewer selected the correct physical measurement or has professional approval authority.

### 7.3 storage.py — persistence and audit

[storage.py](backend/src/foundation_mvp/storage.py) stores projects under a validated 32-hex identifier. It writes project metadata using a temporary file followed by replacement, reducing exposure to half-written JSON.

A project contains active source registrations, its latest job/results, output registrations and audit history. Original source bytes use generated filenames separate from display names.

The threading lock is appropriate for this single-process local application; it is not a cross-process database transaction. Multiple backend workers are not supported.

On restart, queued/running jobs become interrupted. The UI can then tell the operator to rerun instead of displaying a permanently running job.

### 7.4 safety.py — input and archive checks

[safety.py](backend/src/foundation_mvp/safety.py) validates leaf filenames and accepted extensions and checks ZIP entries before working copies are made.

The current policies include:

- 600 MiB upload limit per file.
- 60 active sources and 2 GiB retained source storage per project.
- ZIP count/expanded-size limits: 2,000 members and 1 GiB.
- Rejection of traversal paths, absolute/Windows-style paths, links, encrypted entries and duplicate member names.
- XLSX safety limits of 25 MiB compressed and 128 MiB expanded.
- A 10 MiB reviewed-input document limit.

Upload acceptance and container validation are different from successful CAD interpretation and engineering validation. The UI shows those states separately.

### 7.5 pipeline.py — orchestration

[pipeline.py](backend/src/foundation_mvp/pipeline.py) coordinates ten named stages:

|Stage|Current behavior|
|---|---|
|Input inventory|Build working inputs from active sources; validate archives and preserve provenance.|
|Drawing inspection|Inspect supported DXFs; register reference-only formats, unit issues, xrefs and unsupported types.|
|Coordinate validation|Record original unit metadata and unvalidated drawing relationships. Supplied reference fits are evaluated when reviewed inputs are processed, before affected candidate results are accepted.|
|Data extraction|Expose retained raw evidence, with combined display caps and explicit truncation issues.|
|Plot and corner matching|Find plot-layer label candidates; do not invent physical corner/outline associations.|
|Input validation|Validate reviewed documents and the actual template.|
|Engineering calculations|Validate source handles/alignment connectivity and calculate supported reviewed candidates.|
|Schedule validation|Generate the remaining final-schedule blocker rather than declaring construction completeness.|
|Excel export|Produce a review copy, or a populated draft if reviewed calculation records exist.|
|Output verification|Build summary/report records and expose outputs whose generation/verification succeeded.|

The worker persists stage states, not artificial percentages. A job can finish as completed_with_issues while its engineering results remain blocked or conditional. Failed processing preserves inputs and records the failed stage.

The pipeline's match-point primitive is not a fully integrated automatic survey/drain/tree matcher. In particular, the current code does not turn nearest raw text into a verified ground or drain association.

### 7.6 cad.py and streaming.py — CAD evidence

[cad.py](backend/src/foundation_mvp/cad.py) uses ezdxf for normal-sized files. It inventories entities/layers/blocks/xrefs and retains supported text, attributes and geometric records with source handles.

[streaming.py](backend/src/foundation_mvp/streaming.py) is selected for files over 80 MiB. It reads ASCII group-code pairs, bounds retained entity data, omits opaque binary/OLE payload from extracted evidence and retains supported modelspace records.

Recognition/counting of an entity type does not mean full semantic geometry support. Hatches, dimensions, splines, legacy polyline structures and nested references are not all expanded into a fully reconciled site model. Neither reader certifies engineering meaning merely because parsing succeeded.

The streaming reader was exercised against all nine supplied DXFs. The main drainage file completed inspection without loading its OLE payload into the extracted evidence model.

### 7.7 Numbered marker extraction

The dynamic blocks contain all four number texts, but entity invisibility flags select one visible number in each relevant block:

|Block|Visible number|
|---|---:|
|*U2|3|
|*U3|2|
|*U4|4|
|*U5|1|

A uniquely visible number, a visible circle centred on the block origin and the relevant marker layer allow a numbered marker candidate to be recorded. The record includes the insert position, visible label handle and an explicit geometric-review status.

This is a stronger result than merely counting INSERTs. It is still not proof that the insert's position is a physical house vertex or that the correct house has been identified.

### 7.8 geometry.py — controlled spatial primitives

[geometry.py](backend/src/foundation_mvp/geometry.py) contains:

- `alignment`: orientation-preserving similarity fit with scale/rotation/translation.
- `transform`: application of that mathematical transform to a point.
- `match_point`: an evidence-preserving point match rule.
- `polygon_corners`: a Shapely helper rejecting invalid/non-four-corner outlines.

Alignment requires at least four distinct, uniquely identified controls and a justified positive tolerance. Training controls must be noncollinear; the last control is held out. Median, nearest-rank p95, maximum and holdout residuals are reported. Degeneracy, duplicate controls and excessive error block acceptance.

In the reviewed pipeline, accepted relationships are used to validate cross-drawing evidence connectivity. Raw drawing coordinates are preserved. The system does not automatically discover all controls, apply a complete reconciled site model or certify that reference labels genuinely represent independent physical controls.

The match primitive accepts exactly one feature within a justified threshold. Multiple candidates are ambiguous even if one is nearer. Automatic site-specific feature associations remain outstanding.

### 7.9 engineering.py — deterministic calculations

[engineering.py](backend/src/foundation_mvp/engineering.py) contains small functions independent of HTTP and React:

|Function|Purpose|
|---|---|
|number|Reject missing, boolean, malformed or nonfinite measurements.|
|rounded|Round to 0.001 m using Decimal ROUND_HALF_UP.|
|minimum_depth|Subtract an explicit reviewed minimum depth from its reviewed ground datum.|
|excavation|Calculate competent-strata pipe/manhole influence from reviewed invert/distance/diameter inputs.|
|select|Choose the lowest candidate using unrounded values, retain tied reasons and return an explanation.|
|brief_example|Reproduce the source brief's independent arithmetic example, clearly labelled.|

Minimum candidate:

```text
reviewed ground elevation − reviewed minimum depth
```

Competent excavation candidate:

```text
trench bottom = invert − 0.300 m
raw clear distance = centre distance − 0.500 m − diameter / 2
candidate = trench bottom + max(0, raw clear distance)
```

The source workbook supplies the zero clamp and the tie priority: WPL, Pipe, Manhole, Geology, Old Trees, New Tree, Min Depth for supported candidates. All tied controlling constraints remain in the result.

A genuinely absent pipe diameter may use the brief's 0.100 m fallback, with a warning. Invalid or conflicting values do not become missing. Manhole diameter has no fallback. The current excavation primitive requires competent-strata confirmation and a reviewed centre distance in the source's 0–3 m assessment scope. It does not silently implement the workbook's different allowance branch for other competency conditions.

Tree/geology/WPL candidate elevations may only be explicitly reviewed inputs. Their full derivation rules are not invented or claimed implemented.

### 7.10 review.py — revision history

[review.py](backend/src/foundation_mvp/review.py) reads the active standalone reviewed-input document and saves validated revisions.

Each save:

1. Requires an explanation and reviewer/review rationale.
2. Creates a new source file; old bytes are retained.
3. Records original/revised IDs and hashes, reviewer, reason and time.
4. Replaces the active JSON registration, not the historical source bytes.
5. Clears stale results/job/output registrations.
6. Requires processing again before fresh results are shown.

Original and revised values can be retrieved from their retained source files; the audit does not merely overwrite a number. Reviewer identity is user-provided and not authenticated professional sign-off.

### 7.11 excel.py — actual template output

[excel.py](backend/src/foundation_mvp/excel.py) contains template inspection, review export, draft mapping and draft export.

The confirmed sheet is `Generic 4 corner output`. Headers are row 8, corner numbers row 9 and data rows 10–300, giving 291 confirmed plot rows.

|Column(s)|Draft content|
|---|---|
|A|Plot identifier|
|B|Reviewed house type, when supplied|
|C|Reviewed finished floor level, when supplied|
|E|Average reviewed corner ground level when all four are known|
|H|Explicit draft/review warning|
|I:L|Corner 1–4 reasons|
|U:X|Corner 1–4 bearing elevations|
|Y|Average bearing level when all four results are available|
|AA:AD|Corner depths below FFL when calculable|
|AE|Average depth below FFL when all four are available|

Review export adds an Automation Review sheet without populating schedule results. Draft export additionally replaces only mapped, relevant output cells with backend values, leaves blocked corner levels/reasons blank and hides unused data rows. The original uploaded template remains unchanged. Unrelated formulas and original style IDs are checked after reopening.

No function may write its output over the source template path. Unknown/inapplicable values are not globally turned into zero or 200. The 200 convention is column-specific and its full mapping remains unresolved.

A populated draft is still incomplete for construction because ancillary inputs/branches and professional confirmation are outstanding. openpyxl does not calculate the remaining workbook formulas or guarantee preservation of every advanced Excel extension.

## 8. Frontend walkthrough

### 8.1 App routes and shell

|File|Responsibility|
|---|---|
|frontend/app/layout.tsx|Application name, page shell, project navigation, skip link and footer.|
|frontend/app/page.tsx|Project dashboard, creation form, project cards and API/error states.|
|frontend/app/projects/[id]/page.tsx|Loads the workspace component for a project identifier.|
|frontend/app/globals.css|Shared Tailwind-based form, table, panel, notice, error and focus styling.|

The workspace uses sections within one project route, with a URL hash retaining the selected section. It is not nine independent server routes.

### 8.2 workspace.tsx — nine sections

|Section|What the operator sees|
|---|---|
|Files|Purpose selector, real file upload, size/type/purpose and separate upload/validation/processing states; source deactivation.|
|Processing|Start action and real stage/job status, with errors and explicit blocks.|
|Extraction|Searchable, paginated raw records with layer, coordinates, handle, text/block and marker candidates.|
|Coordinates|Unit metadata, validated/unvalidated status, available residuals and reference evidence.|
|Plots & corners|Label-only or reviewed plots and detailed corner records.|
|Reviewed inputs|Advanced JSON editor with server validation, revision reason and audit-preserving save.|
|Calculations|Backend bearing levels/reasons, conditional review status and a source/step detail dialog.|
|Review issues|Severity/category/plot/source filtering and impact/next action.|
|Outputs|Backend counts, incomplete-construction warning and real registered file downloads.|

The component polls active project status every 1.5 seconds. It cancels superseded result requests, uses no-store API reads and refreshes project metadata after mutations. It does not invent elapsed progress percentages.

### 8.3 review-editor.tsx

This is an advanced document editor, not an automatic engineering correction wizard. It loads the current standalone JSON, rejects malformed JSON, sends a complete schema-validated revision with a change reason and refreshes project state after a successful save.

It starts empty when no reviewed document exists; it does not silently seed a project with synthetic measurements. The labelled test fixture is uploaded explicitly by the operator.

### 8.4 lib/api.ts and lib/schemas.ts

`api.ts` centralizes the backend URL and fetch/error behavior. The default is http://127.0.0.1:8000, configurable through NEXT_PUBLIC_API_BASE_URL. It reads the `{data: ...}` envelope, handles structured errors, validates successful data using Zod and reports unavailable/malformed responses clearly.

`schemas.ts` describes the frontend's expected project, file, job, extraction, coordinate, plot, issue and calculation shapes. TypeScript helps development; Zod checks real runtime responses. Neither replaces backend validation.

Downloads request an actual registered backend output and create a browser file download from the returned bytes.

### 8.5 UI components and accessibility

The local Button component uses Radix Slot and variant utilities. The calculation detail dialog uses Radix Dialog for modal focus/keyboard behavior and explicit title/description/close control.

Forms have labels, tables have headers/captions where implemented, status text accompanies color, focus styling is visible and the layout wraps on smaller screens. These are implemented accessibility measures, not a claim that a full accessibility audit has passed.

## 9. API contract and one complete request trace

Important routes are:

```text
POST   /api/projects
GET    /api/projects
GET    /api/projects/{project_id}
POST   /api/projects/{project_id}/files
DELETE /api/projects/{project_id}/files/{file_id}
POST   /api/projects/{project_id}/process
GET    /api/projects/{project_id}/jobs/{job_id}
GET    /api/projects/{project_id}/extraction
GET    /api/projects/{project_id}/coordinates
GET    /api/projects/{project_id}/plots
GET    /api/projects/{project_id}/calculations
GET    /api/projects/{project_id}/calculations/{result_id}
GET    /api/projects/{project_id}/issues
GET    /api/projects/{project_id}/reviewed-inputs
POST   /api/projects/{project_id}/reviewed-inputs
POST   /api/projects/{project_id}/export
GET    /api/projects/{project_id}/outputs/{output_id}
```

The export POST returns an available draft registration or a conflict when none exists; it is not a final-construction approval endpoint. Workbooks are generated during processing.

For one calculation row, the path is:

1. An uploaded DXF is retained and inspected.
2. An explicitly uploaded/revised reviewed document references the actual drawing filename and retained entity handles.
3. The backend checks schema, sources, alignment connectivity where needed and applicability decisions.
4. The engineering functions produce candidates and choose a controlling result.
5. The result, trace and issues are persisted.
6. GET calculations returns backend data to the frontend client.
7. React displays the level/reason; the dialog displays inputs/steps/sources.
8. The exporter uses the same backend result in the mapped Excel cell.

For example, the synthetic TEST-R2G corner 1 result maps to I10=`Pipe` and U10=`97.950`. There is no separate TypeScript calculation deciding that value.

## 10. Worked example and its evidence boundary

The independent source-brief example is:

|Step|Value|
|---|---:|
|Reviewed ground datum for the example|98.980 m|
|Minimum depth|0.900 m|
|Minimum candidate|98.080 m|
|Drain invert|98.200 m|
|Trench bottom after 0.300 m allowance|97.900 m|
|Pipe centre distance|0.600 m|
|Competent-strata working room|0.500 m|
|Diameter / half diameter|0.100 m / 0.050 m|
|Clear distance|0.050 m|
|Pipe candidate|97.950 m|
|Controlling result|97.950 m, Pipe|

This validates the implemented arithmetic against the brief's issued example. It does not validate every site drawing, tree rule or physical association.

The synthetic DXF contains four explicit points and one line. The accompanying JSON explicitly supplies reviewed test constraints. A successful synthetic run demonstrates file/API/calculation/draft plumbing once locally verified; it is not an automatic extraction claim for the real housing site.

## 11. Storage, output and restart behavior

```text
 data/working/<project-id>/
 ├── project.json
 ├── sources/<generated-file-id>.<extension>
 └── runs/<job-id>/
     ├── generated working copies
     ├── foundation-review-only.xlsx OR foundation-draft-schedule.xlsx
     └── validation-report.json
```

Three useful output distinctions are:

- Raw source evidence/report: inspectability, not verified engineering results.
- Review-only workbook: issues and candidates attached to a copy of the original template.
- Draft schedule: confirmed result columns populated from reviewed conditional results; incomplete construction status retained.

Removing an active input or saving a revision invalidates displayed results and output links, while historical bytes remain. The current UI exposes the latest job, not a full version-history browser. Retention/cleanup and backups are manual.

## 12. Testing and evidence files

|Test source|Coverage|
|---|---|
|backend/tests/test_core.py|Calculation/error rules, controlled geometry, archive safety, local storage, job lifecycle and basic inspection regression.|
|backend/tests/test_completion.py|Streaming records, visibility, OLE handling, EOF/nonfinite errors, MTEXT/attributes, draft mapping and immutable revisions.|
|backend/tests/test_integration.py|Real-library/API tests for CAD, Shapely, schema, actual workbook output/reopen, upload/job/results/download and revisions. These were skipped here because dependencies were absent.|
|frontend/tests/*.test.*|API boundary/errors, dashboard, uploads, calculation dialog, issue filters, downloads and review editor. Written, not executed here.|
|frontend/tests/e2e/workflow.spec.ts|Real-backend browser journey with synthetic inputs and the actual template; downloaded draft reopened with openpyxl. Written, not executed here.|

Executed records are in outputs/offline-test-results.txt, frontend-syntax-check.txt, python-compilation.txt, launcher-syntax-check.txt and streamed-source-evidence.json. [docs/testing.md](docs/testing.md) gives the accurate current status.

The code does not generate expected results from its own output and call them independent truth. The brief and deliberately specified small synthetic cases provide independent expected values. A trusted full client schedule is still needed for broader validation.

## 13. Setup and development helpers

|Helper|Role|
|---|---|
|scripts/setup.sh|Check runtime prerequisites, create the application venv, install dependencies and prepare frontend environment settings.|
|scripts/run-backend.sh|Start the single local Uvicorn process; load a trusted local .env if present.|
|scripts/run-frontend.sh|Start Next development server.|
|scripts/start-local.sh|Check default ports, launch both, write logs and stop its child services on exit.|
|scripts/check_environment.py|Report required Python imports and command availability without exposing secrets.|
|scripts/inspect_sources.py|Read-only original-pack audit.|
|scripts/process_source_evidence.py|Exercise the bounded reader against all nine archive members and save evidence summary.|
|scripts/create_fixture.py|Create the explicitly synthetic fixture, separate from client evidence.|
|scripts/create_source_review.py|Create/check the source-inspection workbook attachment through ZIP/XML, not the runtime openpyxl exporter.|

Backend dependencies are pinned in requirements.txt/pyproject.toml; frontend direct dependencies are pinned in package.json. No resolved transitive lockfile was fabricated after failed registry access. The installation guide explains subsequent npm lockfile generation and platform-specific startup.

## 14. What remains before a final client release

The remaining work has two distinct parts.

### Runtime verification

Install dependencies on a network-enabled machine, run backend/API tests, full TypeScript checking, Next build, Vitest and real-backend Playwright tests. Fix observed failures and record actual results. Service startup, workbook opening and browser behavior must be demonstrated rather than inferred from source syntax.

### Engineering/source completion

Validate actual units/control points; establish physical plot/corner/outline associations; confirm survey and service measurement associations; obtain the missing tree/planting references; confirm geology/WPL/foundation/slab/ancillary requirements and all workbook branches; validate against an independently issued expected schedule.

There is no automatic production DWG converter, PDF geometry reader, complete tree-rule engine, full site semantic matcher, authenticated professional sign-off, database, multi-user deployment, Docker deployment or verified construction schedule hidden elsewhere in the repository.

## 15. Suggested reading order

1. LOCAL_SETUP_AND_WORKFLOW.md — install and operate.
2. This walkthrough — understand implementation and responsibilities.
3. docs/requirements.md and docs/coordinate_mapping.md — actual source findings.
4. docs/data_dictionary.md and docs/calculation_specification.md — inputs, arithmetic and output semantics.
5. docs/api.md — integration boundary.
6. docs/testing.md, docs/edge_cases.md and docs/limitations.md — verification and remaining work.
7. VIDEO_DEMO_PRESENTATION_SCRIPT.md — present the implementation with accurate narration and screen actions.
