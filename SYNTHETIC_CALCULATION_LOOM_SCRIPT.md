# Loom Demo Script — Engineering Calculation Walkthrough

**Target length:** 6–8 minutes  
**Audience:** Kieran McKeever  
**Purpose:** Demonstrate the end-to-end upload, review, calculation and Excel draft flow with explicit synthetic inputs. The master Excel template is the supplied template; all house, ground, pipe and calculation values below are synthetic and are not measurements from Wigston.

## Before recording

Use a fresh project called **Synthetic calculation demo**. Upload these three files:

1. `backend/tests/fixtures/synthetic-house.dxf` — choose **Foundation layout**.
2. `backend/tests/fixtures/synthetic-reviewed-inputs.json` — choose **Engineer-reviewed input JSON**.
3. `2 Template/MASTER Foundation Schedule.xlsx` — choose **Existing Excel template**.

The DXF has four synthetic points and one synthetic line. The JSON explicitly supplies synthetic corner inputs and the Pipe case. Keep the labels “synthetic” visible in your narration; do not present the calculation as a result from the Wigston drawings.

## 1. Opening and create project — about 45 seconds

**[ON SCREEN: Open `http://127.0.0.1:3000`. Enter “Synthetic calculation demo” and click “Create project.”]**

**SAY:**

Hi Kieran. I’ll show the prototype’s end-to-end calculation and Excel draft workflow using a small synthetic test case. I’m using synthetic inputs because the actual Wigston drawings still need reviewed plot, corner and constraint associations before they can support a calculation.

The workbook is the supplied master template. The drawing values and calculated result in this example are test data, not site measurements.

## 2. Upload the inputs — about 60 seconds

**[ON SCREEN: Open Files. Upload the three files using the dropdown purposes listed above. Show their names and categories.]**

**SAY:**

The DXF contains four test points and one test line. The reviewed-input JSON supplies a synthetic plot, TEST-R2G, and explicit corner and constraint inputs. The Excel file is the existing master template.

Uploading a file means the app accepted it. The DXF by itself does not prove physical corner associations; this test makes those inputs explicit in the synthetic JSON so we can demonstrate the calculation path.

## 3. Run processing and inspect evidence — about 60 seconds

**[ON SCREEN: Open Processing, click “Start processing,” and show the actual saved stage statuses. Then open Extraction.]**

**SAY:**

The backend processes the uploaded files and records each stage. I can inspect the drawing evidence with its source file, layer and entity handle. The processing status tells us what ran; it doesn’t mean this synthetic example represents a verified site result.

## 4. Walk through the engineering calculation — about 2 minutes

**[ON SCREEN: Open Calculations. Select TEST-R2G, corner 1. Click “View calculation.” Point to inputs, candidate levels, steps, sources and controlling constraint.]**

**SAY:**

For corner one, the synthetic ground level is 98.980 metres and the supplied minimum foundation depth is 0.900 metres. Subtracting the minimum depth gives a candidate level of 98.080 metres.

The synthetic drainage input gives an invert of 98.200 metres. Subtracting the 0.300 metre trench allowance gives a trench bottom of 97.900 metres.

The pipe centre distance is 0.600 metres. After subtracting 0.500 metres of working room and half of the 0.100 metre pipe diameter, the clear distance is 0.050 metres. Adding that to the trench bottom gives a Pipe candidate of 97.950 metres.

The calculation selects the lower bearing elevation, because that requires the deeper foundation. So Pipe controls this synthetic corner at 97.950 metres. The minimum-depth candidate was 98.080 metres.

The calculation is performed by the Python backend. This detail view shows the supplied inputs, source references, candidate levels and reason for the result. It demonstrates traceability for this test case; it does not validate the same measurements against the actual Wigston drawings.

## 5. Show remaining review status — about 45 seconds

**[ON SCREEN: Open Review issues and show the actual current messages.]**

**SAY:**

The run can still complete with review issues. A calculation for an explicitly supplied synthetic corner does not establish a complete construction schedule or resolve the outstanding engineering and workbook questions for the real project.

## 6. Show the Excel draft — about 75 seconds

**[ON SCREEN: Open Outputs. Download the current `foundation-draft-schedule.xlsx` and `validation-report.json`. Open the workbook, show Automation Review, then `Generic 4 corner output`, row 10.]**

**SAY:**

The exporter uses a copy of the supplied master template. Automation Review explains the draft status. In the Generic 4 corner output, row 10 is the synthetic TEST-R2G example.

For corner one, the controlling reason is Pipe in cell I10 and the bearing level is 97.950 in U10. The other synthetic corner levels are 97.940, 97.870 and 97.900 metres in V10 through X10. The workbook also shows the explicit draft warning. This is a populated draft for review, not an approved construction schedule.

The validation report provides the machine-readable run details. Unknown or unconfirmed site values are not made up to fill the template.

## 7. Close — about 30 seconds

**[ON SCREEN: Return to the project summary.]**

**SAY:**

That’s the calculation workflow: explicit inputs, traceable candidate levels, a controlling constraint and a draft in the existing workbook layout. The next step for a real Wigston calculation is to have the engineering inputs and drawing associations reviewed and confirmed.

Thanks for watching. I’d welcome your feedback on the calculation trace and the draft workbook.

## Accuracy notes

- The `97.950 m / Pipe` result is the synthetic reproduction of the brief example, not a result extracted from Wigston.
- The synthetic JSON marks its test conditions explicitly. Do not relabel it as engineer-approved client data.
- Expected corner levels are 97.950 (Pipe), 97.940 (Min Depth), 97.870 (Min Depth) and 97.900 (Min Depth).
- If the live UI, workbook or report differs, describe the actual output on screen rather than reading an expected value as though it were live.
