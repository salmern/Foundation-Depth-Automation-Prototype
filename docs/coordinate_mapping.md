# Coordinate investigation

No client cross-drawing transformation is accepted.

|Supplied DXF|$INSUNITS|Observed evidence|
|---|---:|---|
|P10989_Layout_xref|4 (millimetres)|Plot 36 text handle 12427 at x=461859334.6546822, y=297491260.8147309|
|P10989_Corner Number_xref|4|Text and dynamic inserts use the same large coordinate magnitude; 679 marker inserts on 4 Corner_100|
|E833 Topo Survey (S584 Rev F)|4|Survey grid text handle 20331 at x=461251.2103561801, y=297697.2634410848; reads 461250 E. Metadata and apparent coordinate magnitudes require confirmation|
|Main external works/drainage|0 (unspecified)|Text handle D837 at x=462227.8824282488, y=297461.7243897425; text is a placeholder SXX.XX IL, not a usable invert|
|Architectural model|0|Coordinates approximately 462000 / 297500|
|Engineering model|0|Coordinates approximately 461000 / 297500|
|As-built lateral survey|4|Coordinates approximately 462000 / 297500; text insertion Z varies and is not necessarily the text elevation|
|Both OS BASE wrappers|0|Each inserts OS BASE; block interpretation needed|

A 0.001 scale from foundation coordinates is a candidate hypothesis only. Units alone cannot validate it, especially where topology/as-built header metadata says millimetres despite metre-like coordinates. No median/p95/max residual is reported for the client drawings because no independent shared references have been validated. These fields are absent/unavailable rather than zero.

The main drainage file retains five model xrefs pointing to DWGs in MODELS; corresponding separate DXF conversions exist, but this is not proof their nested placements, units or revisions align. Corner file xrefs the layout. No external path is followed automatically. Original xref strings are retained.

## Implemented validation primitive

An orientation-preserving similarity (scale, rotation, translation) is fit to all but the final control point. At least four named controls are required; training controls must be noncollinear and identifiers unique. The final control is independently held out. All control residuals must meet an explicitly justified positive metre tolerance. Median, nearest-rank 95th percentile, maximum and holdout residual are returned. Reflection, degeneracy and excessive residuals block acceptance. The fit does not infer a professional tolerance or certify reference independence from geometry alone.

Unit, reference selection, tolerance and reference evidence remain the reviewer's responsibility. Synthetic tests cover rotated/scaled/translated data, reflection, outliers, collinearity, duplicate references and missing controls. The primitive does not automatically discover controls in these drawings.

## Matching

The point-match primitive records every alternative, distance, threshold and justification. Exactly one candidate within a justified threshold is required; multiple candidates are ambiguous even if one is closer. No nearest-elevation-text rule, arbitrary survey interpolation or drainage-gradient inference is applied to client drawings. Verified site matches: zero.

## Follow-up visibility finding

Entity code 60 resolves the formerly ambiguous dynamic number labels: *U2 shows 3, *U3 shows 2, *U4 shows 4, *U5 shows 1. Each marker block has a single visible circle centred at its block origin. The new reader emits numbered marker candidates with insertion coordinates and the label source handle. It does not declare them physical house corners or associate them with plots. The actual counts are 170 markers each for numbers 1, 3 and 4, and 169 for number 2. All nine source DXFs were exercised with the bounded reader; see outputs/streamed-source-evidence.json.
