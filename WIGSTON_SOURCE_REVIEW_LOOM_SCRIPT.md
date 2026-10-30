# Loom Demo Script — Wigston Source Review

**Target length:** 6–8 minutes  
**Audience:** Kieran McKeever  
**Purpose:** Show how the prototype inspects the actual Wigston source pack, what evidence it surfaces, and which engineering decisions remain open. This is a source-review demonstration, not a completed foundation calculation or construction schedule.

## Before recording

- Start the local application and create a fresh project called **Wigston source review**.
- Upload the converted drawing package `dxf files.zip` from the `Contractor brief` folder. It contains nine DXFs. Since it is a mixed-purpose archive, choose **Additional references** and explain that this category applies to the ZIP as a whole, not to each drawing inside it. Do not upload the same DXFs a second time individually.
- Upload `1 Drawings/P10989_01H - foundation drawing.pdf` as a reference and `2 Template/MASTER Foundation Schedule.xlsx` as the existing Excel template.
- The DWGs were converted to DXF working copies because the prototype inspects DXF; direct DWG processing is unsupported. Keep the original DWGs unchanged. Do not upload a reviewed-input JSON or synthetic fixture for this source-review demo.
- Process the project before recording if you want to avoid waiting on the large drainage drawing. Rehearse once and show the actual current run and outputs.

## 1. Opening and create project — about 45 seconds

**[ON SCREEN: Open `http://127.0.0.1:3000`. On the Projects page, enter “Wigston source review” and click “Create project.”]**

**SAY:**

Hi Kieran. I’m going to show you the prototype using the actual Wigston source pack. I’ll start by creating a fresh project, then upload the drawing evidence and existing schedule template.

This walkthrough focuses on what the system can inspect and what still needs an engineer to confirm. It does not present unverified drawing matches as completed foundation calculations.

## 2. Explain the inputs — about 60 seconds

**[ON SCREEN: Open Files. Upload the DXF ZIP, the foundation PDF and the master Excel template. Show the file list.]**

**SAY:**

The drawings I was given were DWG files. I converted working copies to DXF because the current prototype reads DXF; it does not process DWG directly. The original DWGs remain unchanged.

The archive contains nine converted drawings, including the foundation layout and corner-number references, topographical survey, drainage drawing, architectural and engineering models, and an as-built lateral survey. I’ve also added the foundation PDF and the existing Excel template.

The ZIP is mixed-purpose, so its category in this file list describes the archive as a whole. It does not prove the engineering role of every drawing inside it. Uploading a file means it was accepted; it does not mean its contents or relationships have been verified.

## 3. Run and show processing — about 60 seconds

**[ON SCREEN: Open Processing. Start the run if needed; otherwise show the completed run and its real stage statuses.]**

**SAY:**

I’ll start the processing run. The backend inventories the inputs, inspects supported drawing evidence, extracts records, checks what can be validated, and prepares review outputs where possible.

The main drainage DXF is large, so the application uses a bounded reader for large ASCII drawings. A processing run can finish while engineering questions remain unresolved. The stage status tells us what the software did; it does not approve the drawing interpretation or certify a construction schedule.

**[ACTION: Let the real statuses finish. If a stage fails or blocks, show its actual message.]**

## 4. Inspect real drawing evidence — about 90 seconds

**[ON SCREEN: Open Extraction. Search or page through records from a selected source file. Point out entity type, layer, coordinates, source filename and handle.]**

**SAY:**

Here is evidence extracted from the actual converted drawings. The table keeps the source drawing, layer and entity handle alongside the extracted text or geometry, so we can trace a record back to its source.

The source review found 679 numbered marker candidates across the converted drawings: 170 each for markers 1, 3 and 4, and 169 for marker 2. Those are visible numbered candidates, not 679 confirmed house corners. The system does not assign them to physical plots automatically.

The same distinction applies to survey and drainage evidence. A text label or a nearby line is evidence to inspect; by itself it does not establish which survey point, drain, invert or house corner it belongs to.

**[ACTION: Use only examples actually visible in the run. Do not claim a specific entity-to-plot match unless it is visibly reviewed and confirmed.]**

## 5. Show coordinates and plot/corner status — about 75 seconds

**[ON SCREEN: Open Coordinates, then Plots & corners.]**

**SAY:**

This is where the source review exposes an important limitation. The drawings do not all declare units consistently, and their coordinate magnitudes do not establish a verified relationship by themselves. The project has no accepted cross-drawing transformation yet.

The marker numbers are visible, but their physical plot and corner associations have not been confirmed. The current source review therefore has zero verified physical plot corners. That is why I’m not showing a calculated foundation level from these drawings.

## 6. Review issues and outputs — about 90 seconds

**[ON SCREEN: Open Review issues and show the actual issues. Then open Outputs. Download and open a report or review-only workbook only if the current run provides it.]**

**SAY:**

The review issues make the remaining work explicit. The open items include confirming coordinate alignment and physical plot/corner associations, linking survey and drainage evidence to the right features, and resolving missing engineering inputs and workbook branches.

If an output is available, it is a review artifact based on the evidence and confirmed mappings available in this run. It is not a completed construction schedule. I’m showing the report so the review trail is visible, not treating a generated spreadsheet as proof that every input is correct.

## 7. Close — about 30 seconds

**[ON SCREEN: Return to the project summary.]**

**SAY:**

This demonstrates the real-source workflow: create a project, inspect the converted drawings, trace extracted evidence, and see which decisions remain open. The next step is to confirm those engineering relationships and inputs, then compare any resulting schedule against an independently checked expected result.

I’d appreciate your feedback on whether this review workflow gives your engineers the right evidence and next actions.

## Recording guardrails

- Do not show the synthetic `TEST-R2G` calculation or quote the synthetic 97.950 m / Pipe result in this real-source walkthrough.
- Say “marker candidate” unless a qualified reviewer has confirmed a physical corner association.
- Use the actual status and issue descriptions shown in the current run; do not read stale or expected statuses as if they were live.
- Do not call a completed processing run a completed engineering result.
- The complete construction schedule remains unverified until the open engineering inputs and workbook mappings are confirmed.
