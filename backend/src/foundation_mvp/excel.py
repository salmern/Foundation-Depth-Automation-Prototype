"""Template inspection and non-destructive review export.
A construction schedule export is blocked until the entire workbook dependency
mapping is confirmed. A review workbook never claims to populate the schedule.
"""
from pathlib import Path
from .engineering import REASONS
SHEET='Generic 4 corner output'
EXPECTED={'A8':'Plot','I8':'Reason for Foundation Depth','U8':'Anticipated Bearing Level of Concrete Foundation'}
def inspect_template(path):
 from openpyxl import load_workbook
 wb=load_workbook(path,data_only=False)
 if SHEET not in wb.sheetnames or 'Input' not in wb.sheetnames:raise ValueError('Required template sheets are missing')
 ws=wb[SHEET]
 for cell,value in EXPECTED.items():
  if ws[cell].value!=value:raise ValueError(f'Template mapping changed at {SHEET}!{cell}')
 for col in ['I','J','K','L','U','V','W','X']:
  if ws[f'{col}10'].data_type!='f':raise ValueError(f'Required output formula missing at {col}10')
 info={'sheets':wb.sheetnames,'mapping':{'plot':'A','reason':['I','J','K','L'],'bearing_level':['U','V','W','X'],'first_row':10,'corner_order':[1,2,3,4]},'hidden_sheets':[s.title for s in wb if s.sheet_state!='visible'],'hidden_columns':{s.title:[k for k,v in s.column_dimensions.items() if v.hidden] for s in wb},'defined_names':list(wb.defined_names),'formula_count':sum(c.data_type=='f' for s in wb for row in s for c in row),'mode':'review_only','warning':'Original template contains formula errors and engineering branches beyond the implemented primitives. Schedule population is blocked; review export preserves original sheets.'}
 wb.close();return info

def export_review(template,target,results):
 if Path(template).resolve()==Path(target).resolve():raise ValueError('Output must not overwrite the source template')
 from openpyxl import load_workbook
 inspect_template(template);wb=load_workbook(template)
 if 'Automation Review' in wb.sheetnames:raise ValueError('Template already has an Automation Review sheet')
 original_formulas={(s.title,c.coordinate):c.value for s in wb for row in s for c in row if c.data_type=='f'}
 original_styles={(s.title,c.coordinate):c.style_id for s in wb for row in s for c in row if c.has_style}
 ws=wb.create_sheet('Automation Review');ws.append(['REVIEW ONLY — ORIGINAL SCHEDULE NOT POPULATED'])
 ws.append(['Dataset',results.get('dataset_kind','drawing_extraction')]);ws.append(['Status',results['status']]);ws.append(['Issue ID','Severity','Category','Plot','Corner','Source file','Source entity','Description','Impact','Next action'])
 def safe(v):
  v='' if v is None else str(v)
  return "'"+v if v.startswith(('=','+','-','@')) else v
 for i in results['issues']:ws.append([safe(i.get(k)) for k in ['id','severity','category','plot_id','corner','source_file','source_entity','description','impact','next_action']])
 ws.append([]);ws.append(['Calculation candidates — engineer-reviewed imports; not a construction schedule'])
 ws.append(['Plot','Corner','Bearing level (m)','Reason','Status'])
 for r in results['calculations']:ws.append([safe(r['plot_id']),r['corner'],r.get('bearing_level'),r.get('reason'),r['status']])
 ws.freeze_panes='A5';ws.column_dimensions['H'].width=65;ws.column_dimensions['I'].width=50;ws.column_dimensions['J'].width=55
 wb.save(target);wb.close()
 verify=load_workbook(target,data_only=False)
 for (sheet,cell),formula in original_formulas.items():
  if verify[sheet][cell].value!=formula:raise ValueError('Original formula changed during export')
 for (sheet,cell),style in original_styles.items():
  if verify[sheet][cell].style_id!=style:raise ValueError('Original formatting changed during export')
 if 'Automation Review' not in verify:raise ValueError('Review output missing')
 verify.close();return {'verified':True,'kind':'review_workbook','schedule_complete':False,'preserved_formulas':len(original_formulas),'name':Path(target).name,'warning':'Review attachment only; original schedule remains unpopulated. openpyxl does not calculate formulas; unsupported Excel extension features may not be retained.'}


def schedule_plan(results):
 """Map reviewed results into confirmed output columns; incomplete cells stay blank.

 This is a DRAFT schedule. Ancillary fields still depend on workbook logic not
 confirmed by the supplied pack, so schedule_complete never becomes true.
 """
 from .engineering import number,rounded
 plots=results.get('plots',[])
 if not plots or not results.get('calculations'):
  raise ValueError('No reviewed calculation results are available for a draft schedule')
 if len(plots)>291:
  raise ValueError('The confirmed template has only 291 output rows (10–300)')
 indexed={}
 for r in results['calculations']:
  key=(r['plot_id'],r['corner'])
  if key in indexed:raise ValueError('Duplicate plot/corner result')
  if r['corner'] not in (1,2,3,4):raise ValueError('Invalid corner number')
  indexed[key]=r
 cells={};calculated=0;seen=set()
 for offset,plot in enumerate(plots):
  pid=plot['plot_id'];row=offset+10
  if pid in seen:raise ValueError('Duplicate plot identifier')
  seen.add(pid);ffl=plot.get('ffl_m');corners={c['corner']:c for c in plot.get('corners',[]) if 'corner' in c}
  cells.update({f'A{row}':pid,f'B{row}':plot.get('house_type'),f'C{row}':ffl,
                f'H{row}':'AUTOMATION DRAFT — ENGINEER REVIEW REQUIRED. Missing corner results are blank; ancillary schedule fields are not confirmed.'})
  levels=[];grounds=[];depths=[]
  for i in range(1,5):
   r=indexed.get((pid,i));level=None;reason=None
   if r and r['status']=='calculated':
    if r.get('reason') not in REASONS:raise ValueError('Invalid output reason label')
    level=rounded(number(r.get('bearing_level'),'bearing level'));reason=r['reason'];calculated+=1;levels.append(number(level,'bearing level'))
   cells[f'{"IJKL"[i-1]}{row}']=reason
   cells[f'{"UVWX"[i-1]}{row}']=level
   depth=rounded(number(ffl,'FFL')-number(level,'bearing level')) if ffl is not None and level is not None else None
   cells[f'{["AA","AB","AC","AD"][i-1]}{row}']=depth
   if depth is not None:depths.append(number(depth,'depth'))
   ground=corners.get(i,{}).get('ground_level_m')
   if ground is not None:grounds.append(number(ground,'ground level'))
  cells[f'E{row}']=rounded(sum(grounds)/4) if len(grounds)==4 else None
  cells[f'Y{row}']=rounded(sum(levels)/4) if len(levels)==4 else None
  cells[f'AE{row}']=rounded(sum(depths)/4) if len(depths)==4 else None
 if any(pid not in seen for pid,_ in indexed):raise ValueError('Calculation references an unknown plot')
 return {'cells':cells,'plots':len(plots),'expected_corners':len(plots)*4,'calculated_corners':calculated,'review_corners':len(plots)*4-calculated,'schedule_complete':False}


def export_draft(template,target,results):
 """Populate the original output layout with conditional results, clearly as draft.

 Only mapped result cells are replaced; unrelated formulas/style ids are checked
 after reopening. Original source bytes are never changed.
 """
 if Path(template).resolve()==Path(target).resolve():raise ValueError('Output must not overwrite the source template')
 from openpyxl import load_workbook
 plan=schedule_plan(results)
 info=export_review(template,target,results)
 wb=load_workbook(target);ws=wb[SHEET]
 for row in range(10,301):
  if ws[f'A{row}'].value!=f'=Input!B{row}':
   wb.close();raise ValueError(f'Output row mapping changed at A{row}')
 allowed=set(plan['cells'])
 formulas={(s.title,c.coordinate):c.value for s in wb for row in s for c in row if c.data_type=='f' and not (s.title==SHEET and c.coordinate in allowed)}
 styles={(s.title,c.coordinate):c.style_id for s in wb for row in s for c in row if c.has_style}
 for coordinate,value in plan['cells'].items():
  ws[coordinate]=value
  if isinstance(value,str):ws[coordinate].data_type='s'
 for row in range(10+plan['plots'],301):ws.row_dimensions[row].hidden=True
 review=wb['Automation Review'];review['A1']='DRAFT SCHEDULE — ENGINEER REVIEW REQUIRED. ORIGINAL OUTPUT LAYOUT POPULATED ONLY WHERE INPUTS ARE REVIEWED.'
 review.append(['Draft plots',plan['plots'],'Calculated corners',plan['calculated_corners'],'Unresolved corners',plan['review_corners']])
 wb.active=wb.sheetnames.index('Automation Review');wb.save(target);wb.close()
 reopened=load_workbook(target)
 try:
  for (sheet,cell),formula in formulas.items():
   if reopened[sheet][cell].value!=formula:raise ValueError('An unrelated formula changed')
  for (sheet,cell),style in styles.items():
   if reopened[sheet][cell].style_id!=style:raise ValueError('Original cell formatting changed')
  for cell,value in plan['cells'].items():
   if reopened[SHEET][cell].value!=value:raise ValueError(f'Draft result verification failed at {cell}')
 finally:reopened.close()
 return info|{'kind':'draft_schedule','name':Path(target).name,'schedule_complete':False,'draft_plots':plan['plots'],'calculated_corners':plan['calculated_corners'],'review_corners':plan['review_corners'],'warning':'DRAFT for engineering review. Known output cells contain backend results; missing corner outputs are blank. Ancillary workbook inputs/branches remain unconfirmed. Not a complete construction schedule.'}
