# API

FastAPI OpenAPI is available at `/docs`. All JSON success responses use `{ "data": ... }`; failures use `{ "error": { "code": "...", "message": "...", "details": [...] } }`. Validation uses 422, missing resources 404, workflow conflicts 409, oversize inputs 413, unexpected failures 500 with no browser stack trace.

|Method|Path under /api|Purpose|
|---|---|---|
|GET|/health|Local service health and blocked schedule-export policy|
|POST|/projects|Create with `{name}`; 201|
|GET|/projects|Project list, file/job metadata and summaries; no raw evidence payload|
|GET|/projects/{id}|Project metadata, latest job, summary, output registrations|
|POST|/projects/{id}/files|Multipart `file`, `category`; immutable source; 201|
|DELETE|/projects/{id}/files/{file_id}|Deactivate source; retain bytes/audit; invalidate results|
|POST|/projects/{id}/process|Queue real workflow; 202 and job id; 409 while any job active|
|GET|/projects/{id}/jobs/{job_id}|Stage state/current stage/error; no fake percentage|
|GET|/projects/{id}/extraction|Raw records; q search, offset ≥0, limit 1–500 (default100)|
|GET|/projects/{id}/coordinates|Unvalidated source metadata and reviewed fit evidence|
|GET|/projects/{id}/plots|Label-only or explicitly reviewed plots/corners|
|GET|/projects/{id}/calculations|Backend candidate results and traces|
|GET|/projects/{id}/calculations/{result_id}|One result with sources/steps/unresolved inputs|
|GET|/projects/{id}/issues|Read-only; severity, plot, category, source filters|
|GET|/projects/{id}/reviewed-inputs|Read the current standalone reviewed document and revision|
|POST|/projects/{id}/reviewed-inputs|Validate a revision, retain old/new values as immutable source files, audit reviewer/reason/time; invalidate stale results|
|POST|/projects/{id}/export|Return available populated draft schedule metadata; 409 if absent. Final construction completeness remains false|
|GET|/projects/{id}/outputs/{output_id}|Download registered existing verified artifact|
|GET|/examples/brief|Clearly labelled independent brief calculation; no project result|

Categories: foundation, topography, drainage, trees, reference, template, reviewed_inputs. XLSX template and reviewed JSON have enforced purposes. Extensions: DXF/DWG/PDF/XLSX/ZIP/JSON. Unknown extension/name rejected. Maximum 600 MiB per upload; 60 active files and 2 GiB retained source bytes per project. ZIPs: 2,000 members / 1 GiB expanded, no unsafe paths/links/encryption/duplicate names. XLSX: 25 MiB compressed / 128 MiB expanded. Normal DXFs use ezdxf; ASCII files over 80 MiB use bounded streaming. Large binary DXF needs a smaller ASCII export. Archive members use generated working filenames and retain archive member provenance; nested ZIPs need separate upload.

A file's container validation is not engineering validation. States include uploaded/container_validated, not_started, queued, processed, processed_with_warnings, failed, reference_only and interrupted. A parsed DXF's raw records remain unclassified evidence.

Jobs: queued → running → completed_with_issues or failed; startup marks orphan queued/running jobs interrupted. Stage states are pending/running/completed/blocked/failed. A workflow can complete while engineering results remain blocked. One single-process worker thread; only the latest job is exposed. Each run's working files/reports remain locally retained.

Source identifiers/handles in JSON are untrusted display text, never file paths to follow. Project/file/output IDs resolve only through validated persisted registrations. The frontend uses a central environment-configured API client, validates successful JSON with Zod and does not calculate bearing elevations.
