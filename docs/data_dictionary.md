# Data dictionary

All internal calculation elevations/distances are SI metres. DXF raw coordinates retain drawing units; no automatic 1,000× conversion is accepted. Missing is `null`, never zero or 200. Inapplicable is an explicit applicability value.

|Record|Fields / meaning|
|---|---|
|Project|32-hex UUID id, printable name (1–120), UTC creation time, status, active files, latest job, summary, outputs, audit|
|Source file|Immutable stored id, original validated name, extension, bytes, purpose, SHA-256, upload/validation/processing states|
|Drawing|Source identifier, `$INSUNITS` code, entity/layer counts, block definitions, xrefs, unsupported types, raw records, truncation flag|
|Evidence|source_file, source_entity handle, layer, entity_type, raw geometry/text/attributes, extraction status. Text is not a verified measurement association|
|Coordinate decision|Original unit metadata, references, similarity a/b/tx/ty, scale/rotation, median/p95/max/holdout residuals, tolerance justification, validation status|
|Match primitive|candidate, distance, all alternatives, threshold, justification, rule, matched/ambiguous/unmatched status|
|Plot|Source plot_id, reviewed/label-only status, corners, source references. No generated workbook-incompatible numbering|
|Corner|Integer 1–4, coordinates, nullable ground elevation, evidence, constraint applicability decisions|
|Candidate|Reason, unrounded elevation, input values, steps, source references, warnings and fallback flag|
|Calculation|Plot/corner id, status, review_status, rounded bearing elevation, exact decimal elevation, controlling constraint(s), explanation, candidates, unresolved inputs|
|Issue|id, error/warning/info, category, description, plot/corner, source file/entity, impact, next_action|
|Output|id, actual relative file path (server only), download name, kind, verified flag, schedule_complete=false|

## Reviewed-input JSON

This is an **additional, explicit manual evidence import**, not drawing-derived automation. It keeps calculations useful while semantic extraction is incomplete. Schema is `ReviewedInputs` in `backend/src/foundation_mvp/models.py`. A complete synthetic example is in `backend/tests/fixtures/synthetic-reviewed-inputs.json`; never present it as client data.

Required top-level fields: schema_version=1, dataset_kind (`synthetic_test` or `engineer_reviewed`), reviewer, review_reason, units=`m`, alignments, plots. Reviewer identity is user supplied, not authenticated professional approval.

Each plot has a unique plot_id, optional ffl_m/house_type and exactly corners 1–4. Each corner has a point, nullable ground_level_m, source references and exactly seven unique constraint decisions (the seven supported labels). Each decision has applicability (`applicable`, `inapplicable`, `unknown`), an explanation and source references. Unknown blocks that corner.

Applicable Min Depth requires explicit minimum_depth_m and corner ground_level_m; the reviewer must confirm its datum/conditions. Applicable Pipe/Manhole requires invert_m, centre_distance_m and competent_strata=true; diameter_m is mandatory for a manhole and may be omitted for a pipe. Other applicable reasons require an explicitly reviewed level_m; these are **not** calculated from invented tree/geology/WPL rules.

Source references use the exact uploaded drawing name and actual extracted DXF handle. Sources from archives use `uploaded.zip::path/member.dxf`. Multiple drawing references require a connected set of independently validated alignments. Each alignment has source_file, target_file, tolerance_m, justification and four or more uniquely named references with source/target metre coordinates and evidence. The last point is a held-out validation control.

Finite numbers only; extra JSON fields rejected. Malformed manifests fail upload. A manifest cannot make the original client schedule export complete. Review decisions and source hashes are retained in local audit/results.

## Reviewed revisions and draft schedules

The Reviewed inputs page and GET/POST reviewed-inputs API support revisions. The validated document and a required change_reason create a new immutable JSON source. Previous source IDs/hashes and revised ID/hash, reviewer, reason and UTC time are recorded. Old source bytes retain original values; no silent edit occurs. Saving clears stale job/results/output registrations. A standalone revision explicitly supersedes JSON embedded in an archive.

Draft schedule mapping is generated from the same backend calculation results, not recalculated by the frontend. Blocked corner cells stay blank. All outputs retain schedule_complete=false until the unimplemented engineering/workbook completion requirements are resolved.
