# Foundation Depth Automation — detailed video presentation script

## 1. Purpose, audience and recording format

This is a **presentation and recording script**, not a claim that a video has been recorded or that the full-stack demo already ran successfully.

Audience: the client, project stakeholders, an engineer reviewing the approach, and a developer taking over the code.

Suggested full recording: **35–40 minutes**. The timestamps below are planning targets; use the time the real application needs. Narration is a script to read/adapt, with room for screen actions and questions. A shorter stakeholder version is provided at the end.

Presentation goal: explain the client's problem, what was actually built, how the code is structured, how a supported reviewed-input workflow reaches a draft in the existing Excel template, what was tested and what remains unresolved.

Keep the following words distinct throughout:

- **Uploaded:** bytes were received.
- **Container validated:** basic file checks passed.
- **Extracted evidence:** CAD data was inspected and source references retained.
- **Numbered marker candidate:** a number was resolved from block visibility; its physical corner association is not automatically verified.
- **Calculated candidate:** implemented arithmetic ran on explicit reviewed inputs.
- **Draft schedule:** known output columns are populated; final construction completeness is not established.

Do not describe synthetic fixture values as client drawing measurements.

## 2. Preparation before recording

### 2.1 Read and prepare

Read [BUILD_WALKTHROUGH.md](BUILD_WALKTHROUGH.md) and [LOCAL_SETUP_AND_WORKFLOW.md](LOCAL_SETUP_AND_WORKFLOW.md) first.

Have these windows ready:

1. Browser at http://127.0.0.1:3000.
2. API documentation at http://127.0.0.1:8000/docs.
3. Code editor opened at foundation-mvp.
4. Terminal in foundation-mvp.
5. Excel or another compatible workbook viewer.
6. A folder for the files you actually download during the recording.

Prepare these exact input files:

```text
backend/tests/fixtures/synthetic-house.dxf
backend/tests/fixtures/synthetic-reviewed-inputs.json
../2 Template/MASTER Foundation Schedule.xlsx
```

For the real-source evidence segment, prepare:

```text
outputs/streamed-source-evidence.json
outputs/streamed-source-run.txt
outputs/original-preservation-check.json
outputs/current-delivery-status.json
```

Use a fresh project so the recording does not accidentally show stale results from an earlier code version. Keep browser zoom/font sizes readable and avoid exposing unrelated local files or secrets.

### 2.2 Run a real preflight

On the machine used for recording, install dependencies and verify the live path before presenting it as a working demo:

```bash
bash scripts/setup.sh
.venv/bin/python -m pytest backend/tests -v
cd frontend
npm run typecheck
npm run build
npm test
npx playwright install chromium
npm run test:e2e
cd ..
bash scripts/start-local.sh
```

The browser tests launch their own services. Stop other application instances before the test run, then start the presentation instance afterward. Read the setup guide for Windows executable-path differences.

Open API health, then create a disposable project and rehearse the three-file synthetic workflow once. Check the actual downloaded workbook, not a workbook left over from another run.

Record the results from your machine. Do not replace the documented development results with “all tests pass” unless that exact larger suite has actually passed on the recording machine.

### 2.3 If the live preflight fails

The development environment could not install dependencies because registry DNS was unavailable. Therefore, a successful FastAPI/Next/openpyxl/browser recording has **not** been established by the existing artifacts.

If the live app does not start, use the offline source-walkthrough version in Section 8. Show the implementation, executed primitive tests and actual DXF evidence artifacts. Say plainly that the full-stack runtime is not being demonstrated. Do not use static images, mocked responses or an edited success screen as a substitute for a real run.

## 3. Recording outline

|Time target|Scene|Screen|
|---|---|---|
|00:00–02:00|Problem and deliverable|Title / project README|
|02:00–04:00|Evidence, scope and actual verification|Status report and source inventory|
|04:00–07:00|Architecture and repository|Build walkthrough and editor tree|
|07:00–09:00|Local startup and API boundary|Terminal, browser and /docs|
|09:00–12:00|Project creation and uploads|Live dashboard and Files|
|12:00–14:00|Backend processing stages|Live Processing|
|14:00–17:00|Extraction, coordinates and plots|Live project sections|
|17:00–20:00|Calculation trace|Live Calculations and engineering.py|
|20:00–23:00|Review issues and auditable correction|Review issues and Reviewed inputs|
|23:00–26:00|Draft workbook and verification|Live Outputs and downloaded workbook|
|26:00–29:00|Actual client drawing evidence|Streaming evidence artifacts / optional real run|
|29:00–34:00|Backend code tour|Editor modules and source references|
|34:00–37:00|Frontend code tour|Editor components and API client|
|37:00–40:00|Tests, limitations and handover|Actual test output and documentation|

If a stage takes longer, keep the real status visible. A time cut is acceptable when captioned “Processing continued; elapsed time …” using the actual elapsed time. Do not invent a progress percentage or conceal a failure.

## 4. Full narration and screen actions

### Scene 1 — 00:00–02:00: Explain the client problem

**Show:** README title, then the first sections of BUILD_WALKTHROUGH.md.

**Say:**

> “This is Foundation Depth Automation, a local web application for reviewing drawing evidence and calculating foundation bearing-level candidates.
>
> “The client currently reads several drawings to establish what controls each of four house corners. The relevant information can include ground levels, nearby drainage and manholes, tree influence and other engineering requirements. The engineer then enters the result and its reason into an existing Excel schedule.
>
> “The purpose of this implementation is to make that workflow more repeatable and traceable. A result should show where its inputs came from, which candidate controlled and which information is still unresolved.
>
> “I will show the supported reviewed-input workflow, the actual code behind it and the existing-template draft output. I will also separate what has been tested from what still needs runtime verification and engineering confirmation.”

**Point to:** the words “evidence review” and “draft schedule.”

**Do not say:** “The application has already verified every corner on the client site.”

### Scene 2 — 02:00–04:00: Show actual source evidence and scope

**Show:** docs/source_inventory.md and outputs/current-delivery-status.json.

**Say:**

> “The work began by inspecting the actual supplied folder. There were seventy-eight source files, including the build brief, the foundation PDF, original DWGs, converted DXFs and the client's Excel template. Original files were preserved; inventory records include their sizes and hashes.
>
> “The pack has nine converted DXF drawings. The main drainage conversion is about four hundred and fifty megabytes because it includes large OLE payloads. A bounded ASCII reader was added and exercised against all nine drawings.
>
> “There are important unresolved source questions. Drawing coordinates and unit metadata are not consistently aligned. Numbered markers are now identifiable, but their physical house-corner and plot associations are not independently verified. Some referenced tree and planting information is absent.
>
> “The documented development test result is fifty-nine passes and eleven dependency-based skips. Python compilation and frontend/launcher syntax checks also passed. Full-stack execution was not verified in that restricted environment because dependencies could not be downloaded.”

**If you have subsequently run full local verification:** add the actual command/date/result from your recording machine, clearly distinguishing it from the development record.

**On-screen caption:** “Raw evidence ≠ verified engineering association.”

### Scene 3 — 04:00–07:00: Explain architecture and code structure

**Show:** the architecture diagram in BUILD_WALKTHROUGH.md; then expand backend/src/foundation_mvp and frontend in the editor.

**Say:**

> “The system has three main responsibilities. The frontend handles user interaction. FastAPI handles the HTTP contract, input validation, projects and jobs. The processing modules inspect source evidence, validate reviewed inputs, calculate candidate levels and create outputs.
>
> “The backend owns the engineering result. The React application does not independently decide which constraint controls a corner.
>
> “The backend modules are separated by responsibility: main.py for API endpoints; models.py for schemas; storage.py and safety.py for persistence and input handling; pipeline.py for stages; cad.py and streaming.py for drawing evidence; geometry.py for controlled spatial primitives; engineering.py for arithmetic; review.py for revisions; and excel.py for template output.
>
> “On the frontend, App Router provides the dashboard and project route. The workspace component presents nine project sections. A central API client handles real requests and validates responses. A separate review editor handles audited input revisions.
>
> “Storage is local files rather than a database. That keeps the local MVP simple, but it means one backend process and one processing job at a time. There is no cloud dependency or AI service in the calculation path.”

**Pause:** briefly highlight each folder; do not scroll through every file without explaining its role.

### Scene 4 — 07:00–09:00: Start and inspect the API

**Show:** terminal with the already successful preflight, then the launcher and /docs.

**Action:** if the app is not already running, run:

```bash
bash scripts/start-local.sh
```

Open http://127.0.0.1:3000 and http://127.0.0.1:8000/docs.

**Say:**

> “The local setup guide contains the exact installation and startup commands. The combined launcher checks the default ports, starts the backend and frontend, writes logs and stops its child services when I press Control C.
>
> “The API documentation is generated from the FastAPI application. These are real endpoints for projects, uploads, processing status, evidence, calculations, reviewed revisions and output downloads.
>
> “The frontend API base URL is configured in frontend/.env.local. Uploaded project data is stored under data/working unless the backend storage location is changed.”

**Point to:** POST /api/projects, POST files, POST process and GET calculations in /docs.

**If any command fails:** stop this live sequence and use the offline alternative, rather than continuing the narration as if startup succeeded.

### Scene 5 — 09:00–12:00: Create a project and upload real test files

**Show:** dashboard.

**Actions:**

1. Enter **Presentation — synthetic installation check**.
2. Click **Create project**.
3. Upload synthetic-house.dxf under Foundation layout.
4. Upload synthetic-reviewed-inputs.json under Engineer-reviewed input JSON.
5. Upload the actual MASTER Foundation Schedule.xlsx under Existing Excel template.
6. Show the file table and its separate status columns.

**Say:**

> “I am creating a fresh project for the presentation. This demonstration is explicitly synthetic: the small DXF and reviewed JSON are test inputs, and the workbook is the client's actual template.
>
> “The DXF contains four point entities and one line. The JSON supplies explicit reviewed corner and constraint decisions so we can exercise the supported calculation and export path without pretending that unresolved client drawing associations have been solved.
>
> “Each file is uploaded to the backend. The backend checks names, types, size limits, signatures or containers and duplicate content. Original bytes are retained under generated filenames with their original display names and hashes.
>
> “Notice that uploaded, container validated and processing status are separate. A file being accepted does not mean its engineering content has been verified.”

**Optional brief failure demonstration:** attempt to upload the same synthetic DXF again. If the expected real duplicate error is returned, show it and explain it. Do not intentionally upload large or harmful files for the recording.

**On-screen caption:** “Synthetic test inputs + actual client template.”

### Scene 6 — 12:00–14:00: Run the processing job

**Actions:** open Processing; click Start processing; keep stages visible.

**Say:**

> “Start processing sends a real request to the backend. The backend saves a job and executes the pipeline in a worker thread, so the browser can continue asking for status.
>
> “The stages cover inventory, drawing inspection, coordinate information, extraction, plot and corner evidence, input validation, calculations, schedule checks, Excel output and verification.
>
> “These are actual saved states. The interface does not show a made-up percentage. A completed stage means its implemented work ran; it does not automatically mean that every engineering question was resolved.
>
> “A completed-with-issues result is expected in this MVP because final construction completeness remains blocked. The important distinction is between finishing a processing run and approving a complete engineering schedule.”

**Show:** the final job status and any blocked/error messages. If the job fails, show the actual message and investigate instead of using the remainder as a success recording.

### Scene 7 — 14:00–17:00: Inspect extraction, alignment and plot evidence

**Actions:** open Extraction, then Coordinates, then Plots & corners.

**Say:**

> “Extraction displays the backend's raw records. For this test there are four points and one line. Each record retains the source drawing, layer and entity handle. The table also supports search and paging for larger datasets.
>
> “On the real pack, the same evidence model includes text, supported geometry, attributes and numbered marker candidates. Extracting a numeric text value is not the same as proving that it belongs to a particular survey point or pipe.
>
> “Coordinates are handled explicitly. Drawings are not assumed aligned because their numbers look similar. Cross-drawing reviewed inputs require a validated connected set of reference relationships. The fit uses independent named controls, a held-out point, a justified tolerance and residual reporting.
>
> “This synthetic test references one drawing, so it does not need a cross-drawing transform to demonstrate the arithmetic. A source can still be shown as unvalidated in the coordinate view; that is not being hidden.
>
> “Plots and corners show the explicitly reviewed records from the JSON. In a raw client run, plot labels can remain label-only, with no invented physical corner assignment.”

**Important:** do not describe a zero/unavailable residual as a measured perfect alignment. Unavailable means no measurement has been established.

### Scene 8 — 17:00–20:00: Explain the calculation with its full trace

**Actions:** open Calculations; select TEST-R2G corner 1; open View calculation. Then show engineering.py briefly beside the browser if possible.

**Say:**

> “For corner one, the backend returns a bearing elevation of ninety-seven point nine-five-zero metres, controlled by Pipe. This is the independently specified example from the brief, reproduced with synthetic reviewed inputs.
>
> “The minimum-depth candidate is ninety-eight point zero-eight-zero: a reviewed ground datum of ninety-eight point nine-eight-zero minus a reviewed minimum depth of zero point nine metres.
>
> “The drain invert is ninety-eight point two-zero-zero. Subtracting the three-hundred-millimetre trench allowance gives ninety-seven point nine-zero-zero.
>
> “The pipe centre distance is six hundred millimetres. Subtracting five hundred millimetres of competent-strata working room and fifty millimetres for half the pipe diameter leaves fifty millimetres of clear distance.
>
> “Adding that clear distance to the trench bottom gives ninety-seven point nine-five-zero. It is lower than the minimum-depth candidate, so it requires the deeper foundation and controls this result.
>
> “The calculation detail retains the input values, candidate levels, steps and source handles. The engine uses Python Decimal, selects using unrounded candidates and rounds the result to three decimals. React is displaying that backend decision.”

**Point to:** source_rule, steps, inputs, reason and sources inside the detail.

**Add:**

> “Missing values are not zero. A genuinely absent pipe diameter can use the brief's one-hundred-millimetre fallback with a warning. A malformed diameter does not get that fallback, and a manhole has no diameter fallback. Tree, geology and working-platform candidate derivations are not invented where their source rules are incomplete.”

**On-screen caption:** “97.950 m / Pipe — source-brief example, synthetic replication.”

### Scene 9 — 20:00–23:00: Show issues and an auditable correction

**Actions:** close the detail dialog; open Review issues and filter severity to error. Then open Reviewed inputs.

**Say:**

> “Issues are returned by the same backend that processes and calculates. They identify severity, category, affected source or corner, impact and next action. An error is not quietly downgraded just to make a project look complete.
>
> “The reviewed-input editor is an advanced JSON editor for explicit engineering evidence. It is not a hidden source of automatic measurements. Each of the seven supported constraints needs an applicability decision and supporting explanation/source reference.
>
> “Changes must be reasoned and retained. A save creates a new immutable document and records the old and new source IDs and hashes, the reviewer, the revision reason and time. It also clears stale results and output registrations, forcing a fresh calculation run.”

**Optional live revision demonstration, only after rehearsing it:**

1. In the synthetic document, change only `plots[0].ffl_m` from **99.2** to **99.3**.
2. Leave dataset_kind as synthetic_test.
3. Enter revision reason: **Synthetic presentation correction to reviewed FFL**.
4. Save; show the success message and invalidated old processing state.
5. Rerun Processing.

**Say:**

> “This is an explicitly synthetic FFL correction. It does not change the reviewed ground or pipe inputs, so the bearing level should remain ninety-seven point nine-five-zero. The derived depth below finished floor level should increase from one point two-five-zero to one point three-five-zero metres. That distinction helps show why an audit needs the original inputs and why a change does not necessarily alter every output.”

Do not alter the pipe distance just to force a different bearing result: that would require new supporting geometric evidence. If you skip this optional edit, keep the original FFL and original expected depth in the workbook segment.

### Scene 10 — 23:00–26:00: Download and inspect the actual draft workbook

**Actions:** open Outputs; download the newest foundation-draft-schedule.xlsx and validation-report.json. Open that exact downloaded file.

**Say:**

> “Only registered files that actually exist are offered for download. The workbook is generated from a copy of the supplied master template, not a redesigned replacement.
>
> “Automation Review is opened first in the draft. It describes unresolved issues and makes clear that this is for engineering review. In Generic 4 corner output, the confirmed mapping puts plot identifiers in column A, reasons in I through L and bearing elevations in U through X.
>
> “For this first synthetic plot, I10 contains Pipe and U10 contains ninety-seven point nine-five-zero. Missing or blocked corner outputs would remain blank, rather than being presented as zero or a verified not-applicable value.”

**Show/check:**

|Cell/feature|Expected for this synthetic run|
|---|---|
|A10|TEST-R2G|
|H10|Explicit automation draft/review warning|
|I10|Pipe|
|U10|97.950|
|V10 / W10 / X10|97.940 / 97.870 / 97.900|
|AA10 without optional FFL edit|1.250|
|AA10 after optional FFL edit to 99.3|1.350|
|Unused data rows|Hidden, not deleted|

**Continue:**

> “Only mapped result cells are replaced with backend values. Unrelated formulas and original style identifiers are checked after the exporter reopens the file. The original source template is not overwritten.
>
> “Other engineering and ancillary workbook branches are still not fully confirmed, and openpyxl does not evaluate the remaining Excel formulas. So this is deliberately a populated draft, not a construction issue. The validation report carries the evidence, issues and calculation records alongside it.”

**Recording note:** if there are several downloads with similar names, verify the newest file explicitly. Do not show an older workbook with the wrong FFL revision.

### Scene 11 — 26:00–29:00: Explain the actual client drawing findings

**Show:** outputs/streamed-source-evidence.json and docs/coordinate_mapping.md.

**Say:**

> “The small browser example verifies the supported plumbing when locally run, but the real source pack is more complex. Here is evidence from the actual nine DXFs, read by the bounded parser.
>
> “The large drainage document includes OLE data that is not retained as extracted engineering geometry. The source file itself remains unchanged. Other supported text and geometric records retain their source identifiers.
>
> “The corner blocks have all four texts in their definitions, but visibility flags identify one displayed number. The resolved mapping is U-two to three, U-three to two, U-four to four and U-five to one. That gives six hundred and seventy-nine numbered marker candidates.
>
> “That number is not the same as six hundred and seventy-nine verified physical house corners. There are also one hundred and six unique plot-label texts in the inspected layout. Those quantities cannot be forced into a complete four-corner schedule without resolving their actual associations.
>
> “The coordinate investigation found different magnitudes and inconsistent unit metadata. We have not accepted a thousand-times scale change simply because it looks plausible. Independent references, tolerances and engineering source confirmation are still needed.”

**Optional real-file run:** create a separate client-source review project and upload the actual archive/template. Show real processing and the resulting blockers. Allow adequate recording time; do not mix it with the synthetic project or describe unresolved client results as the example's successful calculations.

### Scene 12 — 29:00–34:00: Backend code tour

**Show:** editor, in the order below. Use function search rather than lengthy scrolling.

|File/function|Screen action|Narration point|
|---|---|---|
|main.py / create_project, upload, process|Highlight endpoint boundaries.|“The API validates requests, stores sources and starts work. It does not contain a second copy of the engineering formulas.”|
|models.py / ReviewedInputs, Corner, Constraint|Show seven decisions and finite numeric types.|“Schema checks enforce complete corner numbering and explicit applicability, but do not replace professional judgement.”|
|pipeline.py / STAGES, run|Show stage names and failure handling.|“This is the orchestrator. It saves real states, retains partial evidence and records errors instead of making up success.”|
|cad.py / inspect|Show reader choice.|“Normal files use ezdxf; large ASCII files use bounded inspection.”|
|streaming.py / entities, annotate_markers|Show omitted OLE groups and visible-label logic.|“The parser avoids retaining opaque OLE payload and resolves visible number evidence without asserting physical corner geometry.”|
|geometry.py / alignment, match_point|Show held-out control and ambiguity rule.|“Controls must be distinct and justified. A closer candidate is not automatically a safe match.”|
|engineering.py / minimum_depth, excavation, select|Show compact deterministic functions.|“All arithmetic and controlling reasons originate here. Supported ties follow the source workbook's priority.”|
|review.py / save_revision|Show new source registration and audit entry.|“Corrections retain old and new values through immutable files and invalidate stale results.”|
|excel.py / schedule_plan, export_draft|Show mapped columns and reopen comparisons.|“The backend maps results into confirmed cells and checks preservation before exposing the output.”|
|storage.py / save, recover|Show temporary replacement and restart state.|“Local JSON persists projects; interrupted jobs do not remain silently stuck.”|

**Suggested connected narration:**

> “The key design decision is separation. A request handler should not also interpret a CAD block and calculate a foundation. The pipeline delegates those responsibilities to smaller modules, and the calculation engine can be tested independently.
>
> “Another important boundary is between structure and meaning. A finite invert value with a valid source handle is structurally traceable; proving that it is the correct invert for the relevant drain is still an engineering association question. The review workflow makes that distinction explicit.
>
> “The local persistence model is intentionally small. It suits a single local operator and avoids introducing a database before there is a requirement for one. It is not a distributed queue or multi-user production architecture.”

### Scene 13 — 34:00–37:00: Frontend code tour

**Show:** app/page.tsx, app/projects/[id]/page.tsx, components/workspace.tsx, components/review-editor.tsx, lib/api.ts, lib/schemas.ts and components/ui/dialog.tsx.

**Say:**

> “The App Router supplies the main dashboard and project route. Inside the project, the workspace component presents nine sections and retains the selected section in the URL hash.
>
> “React state handles the creation form, uploads, selected section and calculation detail. Active job metadata is refreshed every one-and-a-half seconds. Superseded result requests can be cancelled, and the client uses no-store requests so that it does not intentionally reuse stale calculation data.
>
> “The API module is the single place for the backend URL, request handling and structured errors. Zod checks that successful responses match what the interface expects. A network failure or malformed response becomes a visible error rather than a successful-looking empty dataset.
>
> “The UI components use Tailwind for a restrained engineering interface, and Radix-based components provide accessible dialog behavior and button composition. The calculation detail is a modal with a title, description and keyboard close behavior.
>
> “The review editor sends a complete revised input document plus its reason to the backend. It does not save critical engineering changes only in browser memory. Downloads likewise request actual backend files; the interface does not fabricate workbooks.”

**Point to:** `NEXT_PUBLIC_API_BASE_URL`, `api(...)`, Zod parsing, the nine tab labels and `DetailDialog`.

### Scene 14 — 37:00–40:00: Testing, limits and handover

**Show:** actual terminal test output; docs/testing.md; LOCAL_SETUP_AND_WORKFLOW.md and BUILD_WALKTHROUGH.md.

For the dependency-free recorded check, from foundation-mvp:

```bash
python3 -m unittest discover -s backend/tests -v
```

**If this is the unchanged development dependency environment, say:**

> “This run discovers seventy tests: fifty-nine pass and eleven integration tests are skipped because their libraries are unavailable. That is the recorded verified result. It is not seventy passing tests.”

**If your recording machine has installed dependencies:** narrate its actual result instead; preserve the distinction from the original development record.

**Continue:**

> “The passing tests cover the source-brief arithmetic, validation failures, fallback restrictions, tie priority, coordinate fit and rejection cases, archive safety, persistence, job failures, streaming behavior, marker visibility, draft mapping and audited revisions.
>
> “There is also written coverage for real-library API and workbook workflows, frontend interactions and a Playwright journey using the real backend. Those larger suites need to be executed in the installed environment before calling the full application verified.
>
> “The remaining engineering work is explicit: validated coordinate alignment, physical plot/corner and feature associations, missing tree/planting information, other ground and working-platform requirements, full workbook branches and comparison against an independently issued expected schedule.
>
> “The handover includes source code, dependency files, fixtures, reports, technical documentation, startup helpers and a step-by-step local guide. The current implementation provides an inspectable review-and-draft workflow. A final construction schedule requires the outstanding evidence and validation to be completed.”

**End screen:**

```text
Foundation Depth Automation
Local evidence review • deterministic calculations • traceable draft output

Start: LOCAL_SETUP_AND_WORKFLOW.md
Build details: BUILD_WALKTHROUGH.md
Verification: docs/testing.md
Remaining questions: docs/requirements.md and docs/limitations.md
```

## 5. Rehearsal acceptance points

Check these before calling your recording a successful live demo:

|Check|Evidence to show|
|---|---|
|Both services are reachable|Actual browser page and API health response.|
|The project is fresh|Its visible name/creation and uploaded file list.|
|Uploads are real|Three selected files appear with backend metadata.|
|Processing is real|A real job request and returned stage/job states.|
|The example is labelled synthetic|Project name, document dataset_kind and narration.|
|The arithmetic is visible|Inputs, steps, candidates, 97.950 and Pipe.|
|Issues remain visible|Final-schedule blocker is not hidden or downgraded.|
|Correction is auditable, if shown|Saved new revision/reason and fresh processing run.|
|Download is current|The newly downloaded file from this run.|
|Workbook values agree|I10 Pipe, U10 97.950; AA10 corresponds to the FFL version used.|
|Limits are accurate|No claim of verified complete client plot matching, full tree derivation or approved construction issue.|
|Tests are reported honestly|Executed command/output, with skips and unexecuted suites named.|

These are rehearsal checks, not evidence that the existing development environment already passed them.

## 6. Presentation questions and suggested answers

### “Does it read DWG directly?”

> “No. Original DWGs are preserved as references. Supported processing uses DXF; no DWG converter is bundled or claimed tested.”

### “Does it read the foundation PDF automatically?”

> “The source PDF was inspected during development, including its text and engineering notes. Production PDF geometry interpretation is not implemented; the supplied layout/corner DXFs provide inspectable CAD evidence.”

### “Are the six hundred and seventy-nine markers verified corners?”

> “No. Visible numbering is resolved, but physical corner placement and association with the correct house/plot need independent geometric validation.”

### “Why are reviewed inputs needed?”

> “The pack does not yet support safe automatic semantic association for every required value. Explicit reviewed inputs allow deterministic calculations and traceable drafts without disguising manual judgement as automatic extraction.”

### “Is the nearest survey text used?”

> “No. Text location alone is not a verified survey point. The code does not silently choose the nearest height label.”

### “How does it choose a controlling constraint?”

> “The backend compares applicable unrounded candidate elevations and chooses the lowest. Supported ties use the observed workbook reason priority and retain the tied candidates in the trace.”

### “Can I use the draft for construction?”

> “The application does not establish that approval. Remaining source, engineering and workbook requirements are explicitly unresolved; the output remains a draft for review.”

### “Is it AI deciding foundation depths?”

> “No. Arithmetic is deterministic Python Decimal code. There is no LLM or external AI service in the processing/calculation path.”

### “Is there a database or login?”

> “Not in this local MVP. It uses persistent local files and is intended for one trusted local operator, one backend process and one active processing job.”

### “Does restarting lose projects?”

> “Projects and sources persist locally. A job interrupted by restart is marked interrupted and must be rerun.”

### “Are all tests passing?”

> “The documented development result is fifty-nine passes and eleven dependency-based skips, with syntax checks also passing. Report any additional locally executed suites separately; unexecuted tests are not passing tests.”

### “How much manual time does it save?”

> “No measured site-wide time-saving study is included. We can demonstrate inspectability, repeatable candidate arithmetic and draft mapping, but should measure real engineer effort after semantic matching and validation are completed.”

## 7. Short stakeholder version: 8–10 minutes

Use the same files and preflight, then compress the presentation:

|Time|Content|
|---|---|
|00:00–01:00|Manual engineering problem and the evidence-review/draft scope.|
|01:00–02:00|Architecture: real frontend, backend-owned calculations, local files.|
|02:00–04:00|Fresh project, three real uploads, actual processing states.|
|04:00–05:30|97.950/Pipe calculation trace and source references.|
|05:30–06:30|Review issues and auditable correction design.|
|06:30–07:30|Downloaded draft in the actual Excel layout.|
|07:30–08:30|Actual nine-DXF evidence and unresolved physical associations.|
|08:30–10:00|Recorded tests, runtime gap, engineering gaps and handover guide.|

Do not remove the synthetic-data label or the draft/final distinction to shorten the presentation. Move the detailed code tour to a separate technical recording if necessary.

## 8. Offline alternative when dependencies/runtime are unavailable

Use this version only as an explicitly labelled **source and evidence walkthrough**.

**Opening narration:**

> “This recording covers the implementation and verified offline evidence. The application services are not running in this environment because package registry access is unavailable, so I will not present a live browser or runtime workbook-export success.”

Show:

1. The repository tree and architecture in BUILD_WALKTHROUGH.md.
2. The API endpoint definitions, request models and frontend API calls in source.
3. `python3 -m unittest discover -s backend/tests -v` and its actual pass/skip result.
4. `outputs/streamed-source-run.txt` and `streamed-source-evidence.json` for the nine real DXFs.
5. The independent example test and engineering.py arithmetic.
6. `schedule_plan` and its passing mapping tests, described as mapping verification rather than an executed openpyxl export.
7. The initial source-inspection workbook and `source-workbook-verification.json`, clearly described as ZIP/XML-verified inspection output, not the runtime populated draft.
8. The local setup guide and the precise outstanding runtime/engineering checks.

Optional command, allowing real processing time:

```bash
python3 scripts/process_source_evidence.py
```

This reads the original archive and writes raw evidence. Do not claim it starts the web application, validates complete client corners or produces a construction schedule.

## 9. Recording deliverables

Suggested names for files you actually create after a successful recording:

```text
Foundation-Depth-Automation-full-walkthrough.mp4
Foundation-Depth-Automation-stakeholder-demo.mp4
Foundation-Depth-Automation-demo-test-results.txt
Foundation-Depth-Automation-demo-notes.md
```

The notes should record the code revision if available, machine/runtime versions, executed preflight commands, actual outcomes, synthetic versus client datasets shown and known limitations at recording time. No MP4/video recording is generated by this Markdown script itself.
