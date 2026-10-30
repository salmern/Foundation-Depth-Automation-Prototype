"""Dependency-free inspection artifact; never populates engineering schedule cells.
This auxiliary script preserves original ZIP parts byte-for-byte except workbook
registration of the added review sheet. Production review export uses openpyxl.
"""
import json,zipfile
from pathlib import Path
from xml.etree import ElementTree as E
BASE=Path(__file__).resolve().parents[1];ROOT=BASE.parent
S='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P='http://schemas.openxmlformats.org/package/2006/relationships'
C='http://schemas.openxmlformats.org/package/2006/content-types'
def main():
 inventory=json.loads((BASE/'docs/source_inventory.json').read_text());drawings=[]
 for path in sorted((BASE/'docs').glob('cad-*.json')):
  d=json.loads(path.read_text());drawings.append({'name':path.stem[4:]+'.dxf','units_code':d['units_code'],'entities':{k:v for k,v in d['entities'].items() if k not in ('SECTION','ENDSEC')},'layers':d['layers'],'xref_count':sum(bool(b['xref']) for b in d['blocks'])})
 issues=[{'id':'SRC-001','severity':'error','category':'coordinates','description':'Foundation x/y are approximately 1,000 times drainage/topography x/y, while unit metadata is inconsistent. No independent control-point fit has been validated.','impact':'Cross-drawing matching and dependent calculations blocked.','next_action':'Confirm units and four independent noncollinear reference points, including a held-out control.'},{'id':'SRC-002','severity':'error','category':'corners','description':'679 numbered candidates on 4 Corner_100. Follow-up streaming inspection resolves visible labels (*U2=3, *U3=2, *U4=4, *U5=1); physical corner and plot association remain unverified.','impact':'No verified four-corner plot mapping.','next_action':'Validate numbered marker positions against actual house outlines and plot identifiers with independent checks.'},{'id':'SRC-003','severity':'error','category':'trees','description':'PDF references FPCR 4848-T-12 tree survey/schedule and planting plans; standalone referenced documents not found in supplied pack.','impact':'Tree constraints cannot be independently established.','next_action':'Supply referenced surveys and confirm influence contours, tree groups and revision.'},{'id':'SRC-004','severity':'error','category':'workbook','description':'Input formulas include Vibro and Ask the Engineer; original template has cached formula errors. Entire dependency mapping is not implemented.','impact':'Complete schedule export blocked.','next_action':'Confirm foundation type, geology, WPL, tree and ancillary inputs; validate against an independently issued schedule.'},{'id':'SRC-005','severity':'info','category':'format','description':'Main drainage DXF is 450,784,383 bytes. The bounded ASCII reader now parses it and the other eight DXFs; OLE payload is excluded from extracted evidence, not removed from sources.','impact':'Raw large-file evidence is available. Unsupported OLE content is not interpreted as engineering geometry.','next_action':'Inspect streamed-source-evidence.json; retain original files and review unsupported entities.'},{'id':'SRC-006','severity':'warning','category':'environment','description':'Python packages and frontend packages unavailable; registry DNS resolution failed in sandbox.','impact':'FastAPI/Next.js runtime, openpyxl export and browser integration are not verified.','next_action':'Install pinned dependencies in a network-enabled environment, run the documented complete tests.'}]
 report={'status':'inspection_only_requires_engineering_review','schedule_complete':False,'plots_verified':0,'corners_calculated_from_client_drawings':0,'inventory_file_count':len(inventory),'drawings':drawings,'issues':issues,'verification':'Read-only ZIP/XML/DXF inspection and pdftotext; follow-up bounded reader exercised against all nine DXFs. No ezdxf, openpyxl or full-stack runtime verification in this environment.'}
 (BASE/'outputs/source-validation-report.json').write_text(json.dumps(report,indent=2))
 rows=[['SOURCE INSPECTION ONLY — ORIGINAL SCHEDULE NOT POPULATED'],['No client plot bearing levels verified. Read with source-validation-report.json.'],['Severity','Issue','Description','Impact','Next action']]+[[i['severity'],i['id'],i['description'],i['impact'],i['next_action']] for i in issues]+[[],['Drawing','Units metadata code','Modelspace entity tags','Xrefs']]+[[d['name'],d['units_code'],sum(d['entities'].values()),d['xref_count']] for d in drawings]
 ws=E.Element(f'{{{S}}}worksheet');sd=E.SubElement(ws,f'{{{S}}}sheetData')
 for index,values in enumerate(rows,1):
  row=E.SubElement(sd,f'{{{S}}}row',r=str(index))
  for col,value in enumerate(values):
   cell=E.SubElement(row,f'{{{S}}}c',r=f'{chr(65+col)}{index}',t='inlineStr');inline=E.SubElement(cell,f'{{{S}}}is');E.SubElement(inline,f'{{{S}}}t').text=str(value)
 original=ROOT/'2 Template/MASTER Foundation Schedule.xlsx';target=BASE/'outputs/source-inspection-review-only.xlsx'
 with zipfile.ZipFile(original) as src:
  changed={}
  workbook=E.fromstring(src.read('xl/workbook.xml'));sheets=workbook.find(f'{{{S}}}sheets');sid=max(int(s.get('sheetId')) for s in sheets)+1
  E.SubElement(sheets,f'{{{S}}}sheet',{'name':'Source Inspection Review','sheetId':str(sid),f'{{{R}}}id':'rIdAutomationReview'})
  rels=E.fromstring(src.read('xl/_rels/workbook.xml.rels'));E.SubElement(rels,f'{{{P}}}Relationship',Id='rIdAutomationReview',Type=R+'/worksheet',Target='worksheets/automation-inspection.xml')
  types=E.fromstring(src.read('[Content_Types].xml'));E.SubElement(types,f'{{{C}}}Override',PartName='/xl/worksheets/automation-inspection.xml',ContentType='application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml')
  # Insert registrations into original XML bytes, retaining all namespace
  # declarations, including prefixes used only inside mc:Ignorable/Requires.
  changed['xl/workbook.xml']=src.read('xl/workbook.xml').replace(b'</sheets>',f'<sheet name="Source Inspection Review" sheetId="{sid}" r:id="rIdAutomationReview"/></sheets>'.encode())
  changed['xl/_rels/workbook.xml.rels']=src.read('xl/_rels/workbook.xml.rels').replace(b'</Relationships>',f'<Relationship Id="rIdAutomationReview" Type="{R}/worksheet" Target="worksheets/automation-inspection.xml"/></Relationships>'.encode())
  changed['[Content_Types].xml']=src.read('[Content_Types].xml').replace(b'</Types>',b'<Override PartName="/xl/worksheets/automation-inspection.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
  with zipfile.ZipFile(target,'w',compression=zipfile.ZIP_DEFLATED) as dst:
   for member in src.infolist():dst.writestr(member,changed.get(member.filename,src.read(member.filename)))
   dst.writestr('xl/worksheets/automation-inspection.xml',E.tostring(ws,encoding='utf-8',xml_declaration=True))
 with zipfile.ZipFile(original) as src,zipfile.ZipFile(target) as out:
  for name in src.namelist():
   if name not in changed:assert src.read(name)==out.read(name),name
  assert out.testzip() is None
  for name in out.namelist():
   if name.endswith('.xml'):E.fromstring(out.read(name))
 verification={'artifact':target.name,'zip_crc_valid':True,'xml_parts_parse':True,'original_sheet_parts_byte_identical':True,'original_styles_byte_identical':True,'openpyxl_verified':False,'excel_open_verified':False,'schedule_populated':False}
 (BASE/'outputs/source-workbook-verification.json').write_text(json.dumps(verification,indent=2))
 print(json.dumps(verification,indent=2))
if __name__=='__main__':main()
