# Requirements and source findings

## Evidence inspected

The workspace contained 78 supplied files, including duplicated expanded drainage packages, two build brief formats, one foundation PDF, one workbook, original DWGs and two ZIPs. No existing application/prototype source or AGENTS.md was found. The existing `.venv` contains pip for a different Python version and a launcher referencing another home directory; it was preserved. No standalone contractor test-answer pack or trusted completed site schedule was found.

`source_inventory.json` records file sizes, SHA-256, byte readability, archive membership and path safety. Nine DXFs inside `dxf files.zip` were inspected by streaming group-code pairs without extracting or modifying them. The 450,784,383-byte main drainage conversion includes embedded OLE objects. PDF text was extracted using local pdftotext. The actual workbook ZIP/XML, formulas, headers, named ranges and column visibility were inspected. JSON audit artifacts are original-source inspection, not ezdxf-certified geometric interpretation.

## Confirmed requirements

- One house row, corners numbered 1–4. Lowest applicable bearing elevation controls; bearing level is not excavation depth.
- Brief: 0.9 m clay minimum. Foundation PDF qualifies this as medium volume-change clay outside vegetation influence, with further construction/geology/WPL criteria.
- Drain: invert minus 0.300 m plus clear distance. Working room 0.500 m for competent founding strata, half diameter deducted from centre distance.
- Brief's missing pipe diameter: 100 mm (0.100 m). A malformed/conflicting value is not missing.
- Foundation PDF service details Y/Z also show manhole diameter, competent allowance 0.5 m and 300 mm below invert. PDF services note assesses corners within 3 m but warns further services and locations between corners may require additional deepening.
- Existing output sheet: `Generic 4 corner output`. Reason labels: Min Depth, Old Trees, New Tree, Geology, WPL, Pipe, Manhole. Actual workbook adds Vibro and Ask the Engineer branches.
- Existing schedule and foundation drawing are issued as a pair.
- Core must be deterministic, local, independent of AI/API keys, and retain source evidence.

## Implemented versus unresolved

|Area|Implemented source|Validation / unresolved work|
|---|---|---|
|Inventory|Read-only audit of actual supplied files, archives and workbook|Completed locally with standard library and pdftotext|
|CAD|ezdxf modelspace inspector, layers, blocks, xrefs, handles, geometry and raw text candidates|Large ASCII reader exercised on all nine actual DXFs; one visible number per marker resolved; physical associations and nested placement remain unresolved|
|Coordinates|Similarity fit with independent held-out control, residuals, rejection cases|Synthetic numeric tests pass; no accepted client transformation|
|Matching|Evidence-preserving point matching primitive rejects multiple in-threshold candidates|No verified site survey/drain/tree associations|
|Calculations|Minimum depth, competent pipe/manhole excavation, candidate selection, tied-reason priority|Primitive tests pass; only reviewed inputs can invoke them; full workbook branches not implemented|
|Excel|Confirmed mapping check; review copy plus populated draft schedule for reviewed results; unrelated formulas/styles preserved|Source written; library unavailable; complete schedule population deliberately blocked|
|API|FastAPI project/upload/job/results/download endpoints; local persistence and audit|Written; dependency-based tests not executed|
|Frontend|Next.js App Router, React/TS, Tailwind, shadcn-style accessible components; real API client and eight workspace sections|Syntax checked; build, runtime and browser flow not verified|
|Outputs|Source validation JSON and template-based inspection review attachment|ZIP/CRC/XML and original-sheet byte preservation checked; no site schedule generated|

## Engineering questions that prevent a complete site schedule

1. Confirm actual source units and independent shared control points. Foundation x/y are approximately 1,000× external/survey coordinates; header units cannot establish alignment.
2. Visibility now resolves *U2=3, *U3=2, *U4=4 and *U5=1. Confirm physical corner locations and plot associations. The 679 marker candidates are not 679 verified house corners.
3. Supply FPCR tree survey/schedule 4848-T-12 and the referenced new-planting documents; confirm revisions, contours, existing/removed/proposed trees and G10 species discrepancy.
4. Confirm ground-point association/interpolation method and tolerances. Elevation text placement alone is not a survey point.
5. Confirm pipe/manhole invert and diameter associations, crossing runs, gradient interpolation and which runs influence a corner. Nearest alone may not be controlling.
6. Confirm geology, WPL, proposed/original ground datum, foundation/slab types and all ancillary schedule fields.
7. Provide an independently issued expected schedule/test answer set and decide safe treatment of incomplete rows.
8. Confirm the full Input-sheet dependency mapping and output policy for Vibro / Ask the Engineer.

The supported review-and-draft workflow is source-implemented. Runtime integration verification and engineering source resolution remain necessary; a fully automated client construction schedule is not established.
