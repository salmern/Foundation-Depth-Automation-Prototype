# Run Foundation Depth Automation locally — setup and complete workflow

This guide explains installation, starting/stopping the application, the first test run, processing the supplied project, reviewing inputs, exporting drafts, and what happens internally.

## 1. What you have and what the application can currently do

The code provides a Next.js web interface and a FastAPI backend. It can manage projects, validate uploads, inspect DXF evidence, extract visible numbered marker candidates, validate explicitly supplied coordinate references, calculate from reviewed corner inputs, record changes, and generate a review workbook or populated **draft schedule** in the client's existing Excel layout.

It does **not** certify a complete construction schedule from the supplied drawings alone. Units/alignment, physical plot-corner association, ground/service associations and some tree/geology/workbook inputs remain unresolved. Unknown inputs stay blocked or blank. A result marked calculated means its supplied candidate inputs passed the implemented calculation checks; it does not mean every site constraint has been independently verified.

Current verification in the development environment: 59 dependency-free tests passed, 11 library/API tests skipped; all nine actual supplied DXFs parsed with the bounded reader, including the 450 MB file. Full FastAPI/Next/openpyxl/browser execution could not be tested because dependency registries were unreachable. Installation/start instructions below are provided for your network-enabled machine; they are not a claim those services were started in that restricted environment.

No AI service, API key, database or cloud account is needed. Internet access is needed once to download Python/npm dependencies, and browser binaries if you run browser tests.

## 2. Understand the folders before installing

Keep the package arranged like this:

```text
Contractor brief/
├── Build brief.pdf
├── Build brief.docx
├── dxf files.zip
├── 1 Drawings/
├── 2 Template/
│   └── MASTER Foundation Schedule.xlsx
└── foundation-mvp/
    ├── backend/
    ├── frontend/
    ├── scripts/
    ├── docs/
    ├── outputs/
    └── LOCAL_SETUP_AND_WORKFLOW.md
```

The web application can accept uploads from any folder. The source-audit scripts and automated integration tests expect the original drawings/archive and workbook in the parent folders shown above. Do not rename or move originals for those tests.

The supplied parent-folder `.venv` is broken and is **not** used. You will create a separate environment at `foundation-mvp/.venv`.

## 3. Install prerequisites on Ubuntu/Linux

Open Terminal. Check:

```bash
python3 --version
node --version
npm --version
```

Requirements are Python 3.11 or newer, Node.js 18.18 or newer compatible with the pinned package versions, and npm. The code uses Next.js 14 and React 18. These are project compatibility requirements, not a recommendation to use an unsupported operating-system/runtime release.

If Ubuntu says venv/ensurepip is missing, install the standard tools using your normal administrator account:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

Install a suitable Node.js version and npm through your normal operating-system or Node version-manager installation. Check the versions above before proceeding. Do not install Python project libraries globally or use sudo pip.

If registry requests show `EAI_AGAIN`, `Could not resolve host`, or `Temporary failure in name resolution`, fix your internet/DNS/proxy settings before running setup. Repeating the installation without restoring connectivity cannot resolve this problem.

## 4. Open the project directory

For the location in the supplied workspace:

```bash
cd "/home/betastack/Desktop/Contractor brief/foundation-mvp"
```

On your own machine, substitute the path where you copied the folder. Keep quotes around paths containing spaces. All following Linux commands assume you are inside **foundation-mvp**, unless a command explicitly changes directory.

## 5. Install application dependencies

### Option A: helper script

```bash
bash scripts/setup.sh
```

This checks runtime versions, creates the project's virtual environment, installs pinned backend dependencies, installs frontend dependencies, creates frontend/.env.local if absent, and checks Python imports. It preserves existing environment settings and original supplied files. It does not install operating-system packages.

If setup succeeds, go to Step 7. If it fails, read the final message and the troubleshooting section below.

### Option B: equivalent manual commands

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
cd frontend
npm install
cp .env.example .env.local
cd ..
.venv/bin/python scripts/check_environment.py
```

Only run the copy command when frontend/.env.local does not already hold your settings. The diagnostic should say `backend_dependencies_available: true`.

`npm install` generates package-lock.json. Subsequent clean installations can use npm ci. The delivery has direct dependency pins but no fully resolved transitive lock because registry access was unavailable during development.

## 6. Check environment configuration

Open **frontend/.env.local**. For the default local setup it must contain:

```dotenv
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

You do not need to edit backend settings for the defaults. Optional backend environment variables are described in `.env.example`. The run-backend helper loads a trusted local `.env` file if you create one; raw uvicorn commands do not load it automatically.

Default storage is `foundation-mvp/data/working`. Default CORS allows http://localhost:3000 and http://127.0.0.1:3000. A single backend worker is required. Keep the service bound to 127.0.0.1; this local MVP has no authentication.

## 7. Start the application

### Option A: one terminal

```bash
bash scripts/start-local.sh
```

Wait for initial frontend compilation, then open:

- Application: **http://127.0.0.1:3000**
- API health: **http://127.0.0.1:8000/api/health**
- Interactive API documentation: **http://127.0.0.1:8000/docs**

The combined helper uses the default ports 3000/8000. If you change ports, use the separate-terminal method and update the frontend API URL/CORS accordingly.

Logs are in `outputs/local-backend.log` and `outputs/local-frontend.log`. Keep this terminal open. Press Ctrl+C in it to stop both services.

### Option B: two terminals

In Terminal 1, inside foundation-mvp:

```bash
bash scripts/run-backend.sh
```

Or, directly:

```bash
.venv/bin/python -m uvicorn foundation_mvp.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
```

In Terminal 2, also inside foundation-mvp:

```bash
bash scripts/run-frontend.sh
```

Or, directly:

```bash
cd frontend
npm run dev
```

Keep both terminals running. Stop each with Ctrl+C. Do not run the combined helper and the separate-terminal commands simultaneously.

## 8. First run: use the clearly labelled synthetic test

Start with this small test to check installation before using the large client files. It uses real uploads, real backend calculations and the actual master workbook; its house inputs are synthetic.

1. Open http://127.0.0.1:3000.
2. Enter a project name such as **Synthetic installation check** and click **Create project**.
3. On Files, select **Foundation layout** and upload:
   `backend/tests/fixtures/synthetic-house.dxf`.
4. Select **Engineer-reviewed input JSON** and upload:
   `backend/tests/fixtures/synthetic-reviewed-inputs.json`.
5. Select **Existing Excel template** and upload:
   `../2 Template/MASTER Foundation Schedule.xlsx`.
6. Wait for each file to appear in the table. Container validation means the file was accepted; it does not mean engineering calculations have finished.
7. Open Processing and click **Start processing**.
8. Wait for the real backend stages to finish. A completed-with-issues status is expected because a final construction schedule is not approved.
9. Open Extraction. This fixture contains four POINT entities and one LINE.
10. Open Calculations. Plot TEST-R2G, corner 1 is independently expected at **97.950 m**, controlled by **Pipe**. The other synthetic levels are 97.940, 97.870 and 97.900 m.
11. Click **View calculation**. Check the input values, candidate levels, source handles and calculation steps.
12. Open Review issues. Read the remaining construction-schedule limitation.
13. Open Outputs. Download **foundation-draft-schedule.xlsx** and **validation-report.json**.
14. Open the workbook. Read Automation Review first. In Generic 4 corner output, row 10 should have plot TEST-R2G, reason Pipe in I10 and 97.950 in U10. The workbook remains a draft, not a construction issue.

If this path fails, do not assume the large client files are the cause. Check the logs and run the integration tests below.

## 9. Understand the calculation example

For the synthetic replication of the source brief:

```text
Ground level                         98.980 m
Reviewed clay minimum depth           0.900 m
Minimum-depth candidate              98.080 m

Drain invert                         98.200 m
Trench allowance                     -0.300 m
Trench bottom                        97.900 m

Distance to pipe centre               0.600 m
Competent-strata working room        -0.500 m
Half of 0.100 m diameter              -0.050 m
Clear distance                        0.050 m

Pipe candidate = 97.900 + 0.050       97.950 m
Controlling candidate                 97.950 m, Pipe
```

The lower bearing elevation requires the deeper foundation. These calculations are done only in Python. React displays the backend's values. The example is not a result extracted from the client's Wigston drawings.

## 10. Process the actual supplied files

Create a separate project such as **Wigston source review**.

Upload the original foundation PDF as a foundation reference, the DXF ZIP containing the converted drawings, and the master workbook. You can instead upload separate DXFs under foundation, topography, drainage and reference purposes. Upload tree information when the missing referenced survey/planting sources are supplied. Do not upload the same ZIP and the same extracted DXFs together; that would create redundant/conflicting evidence.

The backend checks archive paths and expansion limits and makes generated-name working copies. It never extracts into the source drawing directories. For a mixed-purpose ZIP, member source names retain the ZIP and member path; its single upload category does not establish each member's engineering role.

Start processing, then inspect:

- **Extraction:** raw geometry, text, layers, attributes, source filenames and handles.
- **Coordinates:** unit metadata, reviewed transformations and residuals; unvalidated alignment blocks dependent use.
- **Plots & corners:** plot-label evidence and any explicitly reviewed plots. Numbered marker candidates appear in raw extraction; their physical corner/plot association still needs review.
- **Review issues:** errors, warnings, missing inputs, xrefs and unsupported entity types.
- **Outputs:** review workbook/report, or a draft schedule once reviewed corner calculations are available.

The main 450 MB ASCII drainage DXF now uses a bounded streaming reader. Opaque OLE bytes are not retained in extracted evidence. The source file itself is unchanged. This allows inspection without pretending the OLE objects or unsupported entities have been interpreted.

Expect blockers from the actual pack: foundation and survey coordinate magnitudes differ, metadata is inconsistent, some required source documents are missing, and no independently verified full plot/corner schedule was supplied. Processing completing does not resolve those facts.

## 11. Review and correct corner inputs

The initial automated extractor provides evidence; it cannot safely infer every engineering association. The reviewed-input document supplies explicit corner/constraint decisions with source references.

### Start with an existing reviewed document

1. Upload the JSON under **Engineer-reviewed input JSON** on Files.
2. Open **Reviewed inputs**.
3. Inspect/edit the document in the advanced evidence editor.
4. Provide the reviewer identity and review rationale inside the document.
5. Enter **Reason for this revision** below the editor.
6. Click **Validate and save revision**.
7. Schema validation errors identify fields to correct. A valid save creates a new immutable source revision and an audit record.
8. Return to Processing and start a new run. Saving invalidates the previous displayed results/download registrations, preventing stale results being reused.

Previous source revisions are retained on disk, not overwritten. The audit links original/revised source IDs and hashes, reviewer, change reason and UTC time. This local app does not authenticate professional credentials.

### Required content

The full schema is in `backend/src/foundation_mvp/models.py`, and a complete example is in `backend/tests/fixtures/synthetic-reviewed-inputs.json`. The data dictionary explains every field. Do not copy synthetic values into real plots.

Each reviewed project document includes:

- schema_version=1; dataset_kind=`engineer_reviewed` for actual reviewed source inputs or `synthetic_test` for synthetic fixtures;
- reviewer, review_reason and units=`m`;
- plots, each with a unique plot_id and exactly corners 1–4;
- each corner's metre coordinates, nullable ground level and actual uploaded file/entity references;
- one applicability decision for each of Min Depth, Old Trees, New Tree, Geology, WPL, Pipe, Manhole;
- a reason and source evidence for each decision;
- independent coordinate-reference evidence for any cross-drawing use.

Use `unknown` when applicability cannot be determined. Do not mark a constraint inapplicable just to obtain a number. Applicable minimum depth needs an explicitly reviewed depth and ground datum. A pipe/manhole needs invert, centre distance, competent-strata confirmation and diameter; only a genuinely absent pipe diameter has the source-defined 100 mm fallback. Other candidate elevations must be explicitly reviewed; automatic tree/geology/WPL derivation is not implemented.

For ZIP entries, the source file name must match the extraction display exactly, for example `dxf files.zip::P10989_Layout_xref.dxf`. A source handle must exist in that drawing. A standalone reviewed revision supersedes any older JSON embedded in an archive, with an information issue recording this choice.

### Coordinate references

A cross-drawing alignment needs at least four uniquely named, distinct source/target reference positions with evidence. Coordinates supplied to the fit are in metres. At least three noncollinear controls are used for fitting; the last control is held out for validation. Supply a positive engineering-justified tolerance; the app will not invent one or widen it to get a match. Median, 95th-percentile, maximum and held-out residuals are shown. Unavailable source drawings, reflection, degeneracy or excessive errors block acceptance.

## 12. What is in the Excel output

Three output types are distinct:

|Output|What it means|
|---|---|
|Review-only workbook|Actual template copied with an Automation Review attachment. Original schedule is not populated because reviewed calculations are absent.|
|Populated draft schedule|Actual Generic 4 corner output layout filled in confirmed result columns for reviewed plots. Incomplete corner outputs stay blank. Ancillary fields/branches still need confirmation.|
|Validation report JSON|Machine-readable evidence, issue list, coordinate decisions, calculations and counts.|

Draft mapping: row 10 onward; plot A, house type B, FFL C, average ground E, explicit draft warning H, reasons I:L, bearing levels U:X, average bearing Y, FFL depths AA:AD and average FFL depth AE. Only mapped output formulas are replaced with backend values. Unrelated formulas and original style IDs are checked after reopening. Unused data rows are hidden, not deleted. The confirmed template supports 291 plot rows, 10–300; larger imports are rejected rather than writing into unrelated rows.

The original uploaded template is never modified. Unknown values are not converted to zero or globally replaced by 200. The template's 200 convention is column-specific. A populated draft is not labelled complete even if all four candidate levels were calculated. openpyxl does not evaluate the remaining Excel formulas.

## 13. How the system works internally, beginning to end

1. **Project creation:** frontend sends POST /api/projects; backend validates the name and creates a local project UUID and metadata.
2. **Upload:** multipart requests send real bytes and purposes. Backend validates names, extensions, signatures, limits, ZIP member safety and duplicates, then retains immutable source bytes and hashes.
3. **Processing request:** backend prevents concurrent conflicting runs, records a job and runs the pipeline in a worker thread. The browser polls saved job states.
4. **Inventory:** working inputs are built from active sources; safe archive members get generated working filenames with original provenance retained.
5. **Drawing inspection:** normal-sized DXFs use ezdxf; large ASCII DXFs use the bounded group-code reader. Layers, blocks, xrefs, text, attributes and supported geometry retain source handles. DWG/PDF remain reference files.
6. **Coordinate validation:** original units are recorded. Supplied reference evidence can validate a similarity transform; unvalidated relationships remain blocked.
7. **Extraction:** raw entities and numbered marker candidates are exposed. Text content and marker visibility are evidence, not proof of all physical engineering associations.
8. **Plot/corner review:** label-only plots remain unverified. Reviewed documents explicitly identify corners, sources and constraint applicability. Required fields and source references are checked.
9. **Calculations:** Python Decimal computes supported candidates and chooses the lowest unrounded elevation. Ties follow the observed workbook priority. Output rounds to 0.001 m.
10. **Schedule validation:** missing/unknown/conflicting conditions become issues. Final construction completeness remains false while required engineering mappings are unresolved.
11. **Excel output:** the actual template is copied; a review attachment is added. Reviewed calculation results may also populate the confirmed output layout as a draft.
12. **Verification:** generated workbooks are reopened, mapped values/formulas/styles checked, then registered for download. Reports are persisted separately.
13. **Browser review/download:** UI requests real backend data and only offers registered existing files. Backend rechecks the file before serving it.
14. **Restart:** projects/files remain on disk. A queued/running job interrupted by restart becomes interrupted; the user must start a fresh run.

Source code responsibilities: frontend/app and components = interface; frontend/lib/api.ts = API client; backend main.py/models.py = API and schemas; pipeline.py = stages; cad.py/streaming.py = drawing evidence; geometry.py = controlled spatial primitives; engineering.py = calculations; excel.py = template output; review.py = revisions; storage.py = local persistence/audit.

## 14. Where data is stored and how to back it up

```text
foundation-mvp/data/working/<project-id>/
├── project.json
├── sources/<generated-file-id>.<extension>
└── runs/<job-id>/
    ├── generated working copies
    ├── foundation-review-only.xlsx OR foundation-draft-schedule.xlsx
    └── validation-report.json
```

Back up `data/working` while no job is running, plus original supplied files. Do not hand-edit project.json to alter results. Removing an input from the UI deactivates it; its bytes remain for provenance. Disk retention/cleanup is manual. Do not delete source revisions referenced by audit records unless you deliberately accept losing that history.

## 15. Run verification on your machine

Stop any existing application servers first for isolated browser tests.

From foundation-mvp:

```bash
.venv/bin/python -m pytest backend/tests -v
cd frontend
npm run typecheck
npm run build
npm test
npx playwright install chromium
npm run test:e2e
```

Playwright starts the real backend/frontend, creates a project, uploads real fixture files plus the actual template, processes, inspects evidence/calculations/issues, downloads the populated draft and reopens it using openpyxl. The Python virtualenv must be in foundation-mvp/.venv. Browser system-library installation may require your normal administrator setup if Playwright reports missing OS libraries.

For checks that run without downloaded libraries:

```bash
python3 -m unittest discover -s backend/tests -v
python3 -m compileall -q backend/src scripts
python3 scripts/process_source_evidence.py
```

The final command reads the original DXF ZIP and writes a raw evidence summary under outputs. It is not a substitute for the real API/browser tests. Do not call skipped tests passed.

## 16. Windows PowerShell setup (alternative)

Install Python 3.11+ with the Python launcher and a compatible Node/npm release, then open PowerShell in foundation-mvp:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
Set-Location frontend
npm install
Copy-Item .env.example .env.local
Set-Location ..
```

Terminal 1:

```powershell
.\.venv\Scripts\python.exe -m uvicorn foundation_mvp.main:app --app-dir backend/src --host 127.0.0.1 --port 8000
```

Terminal 2, inside foundation-mvp:

```powershell
Set-Location frontend
npm run dev
```

Open the same local URLs. No environment activation script is needed. Bash helper scripts and the current Playwright launcher use Linux virtualenv paths; on Windows start services manually and adapt the Playwright Python executable paths before browser testing. Windows runtime has not been tested in the development environment.

## 17. Troubleshooting

|Problem|Action|
|---|---|
|Missing ensurepip / venv creation fails|Install the OS python3-venv package, then recreate only foundation-mvp/.venv if that newly created environment is incomplete. Preserve the parent source folder.|
|pip cannot find any versions / npm EAI_AGAIN|Check internet, DNS, proxy and package index configuration. Run setup again after connectivity is restored.|
|ModuleNotFoundError: fastapi / uvicorn|Use foundation-mvp/.venv/bin/python, not the broken parent environment or global Python. Install backend/requirements.txt.|
|next not found|Run npm install inside frontend; check installation finished successfully.|
|Port 3000/8000 in use|Stop the older app instance. Use only one combined launcher or one pair of terminals.|
|Cannot reach backend|Check API health, backend terminal/log, API base URL and CORS. Restart frontend after changing .env.local.|
|Template rejected|Use the actual MASTER Foundation Schedule.xlsx. Changed headers/sheets/output references are deliberately rejected.|
|Duplicate upload|Remove the obsolete active file first. Retained source bytes remain in audit history.|
|Job interrupted after restart|Sources are retained. Start processing again; do not manually mark a job completed.|
|No calculations|Review issues and supply validated reviewed corner/constraint evidence. Raw drawing upload alone does not establish every engineering input.|
|No draft schedule|Need at least reviewed calculation records and a validated template. A reference-only run produces a review workbook/report.|
|Blank draft corner cells|Input is missing/blocked. Check Review issues; blank does not mean zero or not applicable.|
|Large file takes time|Check actual job stages and logs. No fake percentage is displayed. Source archive decompression and streaming may take minutes.|
|Process terminates from memory pressure|Use a machine with more free memory or separate smaller source exports. Parser threads are not OS-isolated worker processes.|
|Workbook contains remaining prompts/formulas|Unconfirmed ancillary template inputs are intentionally not invented. Draft warnings explain remaining review requirements.|

## 18. Before treating any site output as final

Resolve the engineering questions in docs/requirements.md and docs/limitations.md, validate alignment and physical associations, supply missing tree/planting/ground/geology information, confirm all workbook branches/ancillary fields, and compare against an independent expected schedule. The app's draft label must not be removed as a substitute for those checks.
