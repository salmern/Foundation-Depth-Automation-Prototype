# Limitations and unresolved work

This delivery is an **incomplete, source-implemented MVP**, not a verified full-stack release and not a completed engineering test pack.

## Environment

Dependency registries could not be resolved from the restricted execution environment. The provided root virtualenv references a different home directory and only contains pip for another Python version. A separate venv bootstrap also failed because system ensurepip is missing. Python source compiled, TypeScript/TSX syntax parsed, and standard-library tests ran. FastAPI startup, Next build/type checking, pytest with real libraries, Vitest and Playwright were not executed. There is no transitive dependency lockfile because package resolution failed. No Docker/hosted deployment is included or claimed verified. Install logs are in outputs.

## CAD and engineering

- Actual DXF streaming inventory is complete for all nine converted files; runtime ezdxf code has not been executed here.
- Files over 80 MiB now use the bounded ASCII DXF reader. The 450,784,383-byte main drainage file and all eight other DXFs were parsed locally. Opaque OLE payload is excluded from extracted evidence, never removed from the source. Large binary DXF still needs a smaller ASCII export.
- Raw entity extraction is not semantic CAD understanding. Number visibility now resolves from entity invisible flags; nested insert transforms, layer inheritance, bulged outlines, unsupported entities, xref placements and dimension semantics are not resolved.
- Plot-layer text candidates are extracted but plot-to-outline/corner association is unverified. Dynamic blocks contain all four texts but only one is visible; numbered marker candidates are extracted, and insertion is still not assumed a physical house corner.
- Ground levels are not assigned from nearest text. Survey points, offset labels, contours and interpolation need a validated source-specific model.
- Drain runs/invert/diameter/manhole associations, gradient interpolation, distance to full influencing geometry and competing service influence remain unresolved. Raw INSERTs/text are available for review.
- No accepted client coordinate mapping. Unvalidated cross-drawing reviewed imports block affected corner calculations.
- Referenced standalone tree/planting sources are absent; tree influence rules and contradictions need engineering resolution. Existing PDF assumptions are evidence, not a licence to invent radii/species.
- Only minimum-depth and competent excavation primitives calculate elevations. Other constraint elevations can only be explicitly imported as reviewed candidates. Reviewer identities are unverified strings; the app does not replace professional sign-off.
- Final construction schedule completion remains blocked. Reviewed corner candidates may populate confirmed columns of the original schedule as an explicitly labelled draft; missing outputs remain blank. Unrelated formulas are preserved. The code never labels a draft or inspection artifact as a completed construction schedule.

## Excel

The actual workbook includes complex foundation/slab/geotechnical branches, cell prompts, formula errors and special labels beyond the seven in the prose brief. Complete dependency mapping and final issue policy are outstanding. Draft output writes only confirmed result columns, leaves blocked corner cells blank, adds row warnings and hides unused data rows. Numeric 200 is column-specific. openpyxl cannot recalculate workbook formulas and may not preserve unsupported extensions/features. Runtime review export verifies formulas/styles after reopening but cannot prove Excel rendering or all advanced feature preservation. Offline inspection workbook verification is ZIP/XML/byte-level only; no claim it was opened by Excel/openpyxl.

## Local operations

One trusted local operator, one uvicorn worker, one processing job at a time. No authentication, multi-user security, cross-process locks, distributed queue or production deployment. Bind to loopback. Source bytes remain after removal for provenance; results from old runs remain on disk but active links are invalidated. No garbage collection/UI deletion of projects; backups/retention are manual. Persistent JSON files are suitable for a local MVP, not concurrent production workloads. A worker thread avoids API event-loop blocking but does not isolate CAD parser memory crashes. Individual records and total evidence have safety caps; truncated evidence produces errors.

Frontend screens, requests, errors, accessibility primitives and test source are implemented, but their runtime behavior is not claimed verified. No fabricated result or hardcoded-success fallback is used by the UI.
