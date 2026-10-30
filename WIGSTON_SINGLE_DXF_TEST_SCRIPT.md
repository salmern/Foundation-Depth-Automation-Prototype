# Loom Demo Script — One Real Wigston DXF

**Target length:** 5–6 minutes  
**Drawing:** `P10989_Corner Number_xref.dxf` from `dxf files.zip`  
**Purpose:** Test the real drawing extraction workflow with one small converted DXF. This is not a full source review and does not generate verified foundation calculations.

## Before recording

1. Open `dxf files.zip` and extract only `P10989_Corner Number_xref.dxf` to a convenient folder. It is about 1.7 MB.
2. Do not upload the ZIP as well as this extracted member; that would duplicate the same source evidence.
3. The dropdown in Files labels the uploaded file's purpose. Choose **Additional references** for this corner-number xref, since it is a reference drawing rather than the main foundation layout. The category does not automatically identify the meaning of every CAD entity.
4. Upload the actual master workbook as well, with **Existing Excel template** selected. Do not add synthetic inputs or the original DWG. The template enables a review-only workbook; it does not provide the engineering inputs needed for calculations.

## 1. Create the project — about 30 seconds

**[ON SCREEN: Open `http://127.0.0.1:3000`. On Projects, enter “Wigston corner-marker test” and click “Create project.”]**

**SAY:**

I’m starting with one real converted Wigston drawing so I can show the extraction workflow clearly. This is a focused test of one source file, not the full multi-drawing project.

## 2. Upload one drawing — about 30 seconds

**[ON SCREEN: Open Files. Select “Additional references” in the purpose dropdown. Upload `P10989_Corner Number_xref.dxf`. Then select “Existing Excel template” and upload `MASTER Foundation Schedule.xlsx`.]**

**SAY:**

This file came from the supplied DWG package. I’m using its DXF working copy because this prototype inspects DXF; direct DWG processing is not supported. I’ve kept the original DWG unchanged.

I’m selecting Additional references because this is the corner-number xref file. That category records the upload purpose. It does not prove that the corner markers have been matched to physical houses. I’ve also added the existing schedule template so the app can create a review workbook. The template supplies the spreadsheet layout; it does not supply plot, corner or engineering measurements.

## 3. Run processing — about 45 seconds

**[ON SCREEN: Open Processing, click “Start processing,” and show the real stage statuses.]**

**SAY:**

I’ll run the file through the backend. The app inventories the upload, inspects the drawing, extracts supported records and reports where more evidence is needed. Because I uploaded only one xref drawing, there is no companion layout here to confirm its external reference placement or map markers to plots. The calculation stage is expected to be blocked because no validated corner inputs were supplied. Adding a template does not change that.

**[ACTION: Show the actual final status and any blocked or warning stages. Don’t describe the run as an approved engineering result.]**

## 4. Inspect the extracted marker evidence — about 90 seconds

**[ON SCREEN: Open Extraction. Search for “Corner 1 marker” or page through the records. Show the text/block, coordinates, source filename, entity handle and status.]**

**SAY:**

The source review for this DXF found 679 visible numbered marker candidates: 170 each labelled 1, 3 and 4, and 169 labelled 2. The extraction view keeps the source entity and handle so a reviewer can trace each candidate back to the drawing.

These are marker candidates, not confirmed physical house corners. A number and marker in a CAD file do not establish which plot or building corner they represent. That needs the companion layout, a validated drawing relationship and engineering review.

## 5. Show the calculation block and review issues — about 90 seconds

**[ON SCREEN: Open Calculations, Coordinates, Plots & corners, and Review issues. Show only statuses and messages present in this run.]**

**SAY:**

With this single file, the app can show marker evidence, but it cannot confirm plot associations or cross-drawing alignment. No corner calculation or construction schedule should be inferred from this test. The template cannot fill in those missing engineering inputs, so the calculation stage correctly reports that no validated corner input was provided.

**[ON SCREEN: Open Outputs. Download and open `foundation-review-only.xlsx` and, if useful, `validation-report.json` from this run.]**

The app can still create a review-only workbook from the template. In this run, `foundation-review-only.xlsx` is verified as a review attachment, but the original schedule remains unpopulated. It is not a calculated draft schedule.

The next step for a full Wigston review is to add the companion layout and other relevant sources, then have an engineer confirm the coordinate relationships and physical associations. This one-file run shows how the prototype makes the evidence traceable before those decisions are made.

Thanks for watching. I’d welcome feedback on whether this extraction and review flow is useful for the drawing review process.

## Accuracy notes

- The source audit for this DXF contains 689 extracted records, of which 679 are numbered marker candidates. The extraction table can contain other records too.
- The current run has 0 plots and 0 calculated corners, with blocking issues for missing reviewed inputs and unresolved xref placement. Read the actual status shown on screen if the run changes.
- The Excel template produces `foundation-review-only.xlsx` for this run. It does not populate engineering results.
- Use the counts above only if the current run shows the same results. Otherwise, read what is on screen.
- Do not show the synthetic TEST-R2G calculation or describe any marker as a confirmed house corner.
- This one-file demonstration does not prove all nine converted drawings align or support a complete schedule.
