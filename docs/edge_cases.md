# Edge case policy and coverage

**Block** means the input, affected corner or complete schedule cannot be treated as valid. **Review** means an explicit warning/manual investigation; it never upgrades an error. **Auto** is safe deterministic handling. Tests marked dependency-based are written but not executed here. Complete schedule export is blocked in every current workflow.

|Case|Policy and implemented behavior|Coverage / outstanding work|
|---|---|---|
|Missing files / empty files|Block start without inputs; empty upload rejected; missing template yields issue|Core/API test source|
|Corrupted files / invalid DXF / unreadable Excel|Reject signatures/ZIP container; catch parser/template failures and emit error|Archive core test; CAD/Excel integration tests unexecuted|
|Unsupported formats|Reject unsupported suffix; DWG/PDF retained as reference with warning|Filename core tests; API tests|
|Duplicate files|SHA-256 duplicate rejected|API test source|
|Duplicate or conflicting revisions|Same-name collision rejected; different-name conflicting revisions not semantically detected: review all sources, no complete schedule|No automatic revision precedence|
|Missing xrefs|Xref paths inventoried; external paths not followed; placement/revision unresolved warnings|Actual audit evidence; runtime inspector code|
|Unsafe archive contents|Block absolute paths, traversal, Windows separators/drives, symlinks, encryption, duplicate names and excessive expanded size/count|Traversal/safe/corrupt archive core tests; further guards below|
|Nested archives|Do not recursively extract; emit warning and request supported files separately|Source implementation; no claim recursive support|
|Unsupported entities|Report entity types; raw inspection never certifies semantic completeness|Actual OLE2FRAME/LEADER/ELLIPSE discovered|
|Invalid geometry / nonfinite geometry|Reject invalid four-corner polygon; nonfinite raw numeric geometry replaced by invalid-geometry evidence and issue|Polygon integration test source; raw parser runtime unverified|
|Missing attributes|Raw INSERT attributes retained; missing semantic fields are not guessed|Automatic schema interpretation unresolved|
|Duplicate/missing plot number|Duplicate same-layer labels emit error; missing label cannot produce verified plot|No geometric plot-number fallback|
|Missing units|Error in drawing inspection; no inferred unit substitution|Actual unit 0 found; coordinate core tests|
|Different origins / scales / rotation|Only independently controlled similarity can be validated|Synthetic fit test passes|
|Reflection / unvalidated transformation|Block cross-drawing reviewed calculations|Reflection/rejection tests pass|
|Missing references / excessive residual|Block fit; no tolerance widening|Core tests pass|
|Incorrect block insertion assumptions|Do not infer corners from inserts; visible numbers now resolved; physical corner association unresolved|Actual source evidence documented|
|Missing / extra corner markers|Label-only plot has no verified corners; reviewed import requires exactly 1–4 once|Schema test source; full automatic association outstanding|
|Multiple possible corners / overlapping plots|No automatic association; block and request geometric review|No implemented overlap solver|
|Multiple nearby survey levels / unmatched features / distant levels|Match primitive requires exactly one in justified radius; no nearest-text elevation assignment|Core ambiguous/unmatched/matched tests pass; no site survey interpolation|
|Multiple nearby drains / ambiguous manholes|No automatic geometry/text association; reviewed candidate evidence mandatory|Real matching unresolved, source candidates inspectable|
|Missing tree data / multiple influencing trees / hedge ambiguity / existing-proposed contradictions|Unknown applicability blocks corner; no invented influence radius or species|Actual missing referenced documents; reviewed schema|
|Candidates beyond justified threshold|Unmatched; do not widen radius|Core test passes|
|Missing required inputs / malformed numbers / unexpected units|Finite schema + Decimal validation; explicit metres; unknown constraints block|Core tests pass; schema/API source tests|
|Missing pipe diameter|Only absent pipe value defaults to 0.100 m, recorded warning|Core test passes|
|Invalid or conflicting diameter|Invalid rejected; conflicting value must be marked unknown by reviewer, never defaulted|Core invalid-value test; automatic text conflict parsing unresolved|
|Missing invert / manhole diameter|Block affected excavation; no manhole fallback|Core no-fallback tests|
|Zero / negative distance|Zero centre distance accepted with clamp/review warning; negative rejected; >3m outside source assessment scope rejected|Core test passes|
|Tied constraints|Retain ties; use observed workbook reason priority|Core test passes|
|No applicable / no valid controlling constraint|Block; missing values not zero|Core test passes|
|Precision / rounding|Decimal comparisons before 0.001m ROUND_HALF_UP|Core test passes|
|Unknown reason / Ask the Engineer / Vibro|Reject unsupported reason labels; full workbook branches unresolved and export blocked|Core unknown-reason test|
|Invalid output value|Finite inputs/geometry, JSON disallows NaN; no output from missing candidates|Core numeric tests; runtime verification pending|
|Missing Excel sheet / changed mapping / missing formula|Template header and required reference formula checks reject export|Excel integration test source|
|Missing or duplicate output rows|Draft writes limited to 291 confirmed rows, duplicate results rejected, unresolved levels/reasons blank; final construction completion disabled|Remaining full mapping unresolved|
|Formula overwritten / formatting changed|Runtime review exporter reopens and compares original formulas/style ids|Integration test source; offline artifact sheet/style parts byte-identical|
|Incorrect reason label|Schema and engine allow only seven exact supported labels|Core tests|
|Workbook cannot reopen|Runtime export fails; no download registered|Integration source tests not executed|
|Differs from trusted expected schedule|No trusted complete answer pack supplied; no golden-file claim|Independently specified brief calculation only|
|Unresolved data presented as complete|All outputs schedule_complete=false; schedule endpoint returns an explicitly draft registration or 409 if absent; UI carries blocker|Code + frontend test source|
|Invalid upload / unsupported type / too large|Backend validates names, suffix, container, sizes, purpose, project quotas; frontend prechecks|Core filename/archive tests; API/UI source tests|
|Network interruption / API unavailable|Central client displays actionable error; no optimistic success|Frontend source tests; runtime unverified|
|Job fails / remains incomplete|Catch failure, preserve inputs, report failed stage; restart marks queued/running jobs interrupted|Storage recovery core test; API failure test source|
|Polling failure|Show error while polling continues; manual refresh available|Implemented; browser test not executed|
|Project not found / invalid id|404 / 422 structured response|Core storage test; API tests source|
|Missing processing results|409 response; UI no-run/active empty states|API/UI tests source|
|Download before file exists / missing output file|Only registered files shown; backend existence/path check with 404|API code; E2E source|
|Stale frontend data|No-store fetches, abort result queries, reset results on new run, refresh on mutations|Implemented; no runtime claim|
|Duplicate processing requests|Lock + 409 for active job or another active project|Implemented; concurrency integration not yet executed|
|Partial success|Completed-with-issues status; stage blocks preserved; candidate results distinct from verified schedule|End-to-end test source|
|Browser refresh during job|Persistent project/job read; polling resumes|Implemented, not browser verified|
|Application restart during job|Queued/running jobs marked interrupted during startup|Core storage test passes|
|Malformed API response|Zod boundary rejects unexpected successful body|Frontend source test|
|API validation error / backend exception|Structured error envelope; client displays message; no browser stack traces|API/frontend test source|

## Completion-pass regression coverage

Additional passing tests exercise actual ASCII point/line parsing, marker visibility/ambiguity, bounded OLE payload handling, malformed EOF, nonfinite geometry, MTEXT segments, attached attributes, known draft column mapping, blank blocked outputs, duplicate/unknown result rejection and immutable audited revisions. Full openpyxl/API tests additionally exercise draft generation and the revision endpoint, but remain skipped until dependencies are installed.
