# Calculation specification

## Supported primitives

Python Decimal is authoritative. No frontend calculation or LLM is involved. Inputs must be finite numbers; missing values are errors. Selection uses unrounded levels; output is rounded to 0.001 m using ROUND_HALF_UP.

### Minimum depth

`candidate = reviewed_ground_level - reviewed_minimum_depth`.

Build brief: 0.900 m clay. Foundation PDF Detail A and clay notes qualify this by ground conditions, vegetation, strata and other criteria. Runtime reviewed imports must explicitly provide minimum_depth_m; this is not a universal site default. Original/proposed ground selection and the entire workbook clay/strata/working-platform logic remain unresolved.

### Drain and manhole excavation (competent strata only)

- trench bottom = invert − 0.300 m
- raw clear distance = centre distance − 0.500 m − diameter / 2
- candidate = trench bottom + max(0, raw clear distance)

The positive-distance example is in both the brief and source PDF Details Y/Z. The zero clamp is present in actual `Input!AZ10` / `BU10`. A negative clear distance is retained in the trace and emits a review warning; no negative influence distance is added.

Source workbook `Input!AW10` uses a 0.750 m allowance when the competency cell is not YES. That branch is inspected but not implemented: competent_strata must explicitly be true. This avoids silently deciding soil competency. Manhole diameter is never defaulted. Pipe diameter omitted (not zero, malformed or conflicting) uses the brief's 100 mm = 0.100 m fallback and records a warning.

Only reviewed nonnegative centre distances ≤3 m are accepted under this source drawing's assessment scope. Further services are not declared inapplicable; the PDF explicitly warns they may matter.

### Selection and ties

Lowest applicable elevation wins. Actual `Input!CV10:CY10` orders equality tests as WPL → Pipe → Manhole → Geology → existing trees (two branches) → New Tree → minimum depth (two branches) → Vibro → Ask the Engineer. Supported tied candidates use that observed priority; all tied constraints are retained. `Vibro` and `Ask the Engineer` are unsupported blocking professional-review cases, never remapped to an allowed label.

### Trees, geology and WPL

No automatic rule is invented. Reviewed candidate elevations may be imported with explanations and actual entity references. Applicability must be explicitly assessed; unknown blocks the corner. A candidate calculation is conditional and does not establish global schedule completeness.

## Independently specified brief example

Ground datum inferred solely for this example: 98.980 m − 0.900 m = minimum candidate 98.080 m. Invert 98.200 m − 0.300 m = trench bottom 97.900 m. Centre distance 0.600 m − 0.500 m − half 0.100 m diameter = 0.050 m. Pipe candidate = 97.950 m. Lowest candidate = **97.950, Pipe**. This automated test reproduces the supplied brief example; it is not extraction from the Wigston drawings.

## Actual workbook mapping / export policy

- Eight sheets: Input; Bellway Budget Schedule; Generic 4 corner output; Drg Extract; Foundation Inspection Sheet; Floor Slab Inspection Sheet; Sheet1; Foundation Inspection Sheet rev.
- `Generic 4 corner output` headers row 8, corner numbers row 9, first data row 10.
- Plot A; house type B; FFL C; reasons I:L; bearing elevations U:X. Row 10 reasons reference Input!CV10:CY10, elevations reference Input!JP10:JS10.
- The meaningful A:BF block has 58 columns, but the sheet's used range extends to CV487. Input extends to KD992. Do not equate used dimensions with the brief's column count.
- Input!AK10:AM10 etc. contain numeric 200 defaults for absent drainage values; WPL X:AA formulas also return 200 for `n`. Some other cells contain text N/A or prompts. **200 is not a universal missing-value code** and must not enter internal calculations. Its complete column-specific mapping remains unresolved.
- Formula caches already include #VALUE! / #DIV/0!. openpyxl does not evaluate formulas. Complete schedule population is blocked until dependencies and safe unresolved-row policy are confirmed.
- API review export copies the actual template and adds Automation Review. When reviewed calculation records exist, a draft schedule also populates confirmed output columns A/B/C/E/H, I:L, U:Y and AA:AE for rows 10–300 (291 plots). Only those relevant output formulas are replaced; unrelated formulas and original style IDs are checked after reopening. Missing corner levels/reasons are blank, draft warnings are written to H, unused data rows are hidden, and Automation Review opens first. No final construction completeness is claimed.
- The separately generated offline `source-inspection-review-only.xlsx` adds an inspection attachment using ZIP/XML, preserving original sheet/style bytes. It is an inspection artifact, not the runtime openpyxl export and not a completed schedule.
