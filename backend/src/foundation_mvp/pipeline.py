"""Background workflow: raw drawing evidence and explicitly reviewed calculations."""
import json,logging,shutil,zipfile
from pathlib import Path
from . import storage
from .safety import archive_members,InputError
from .engineering import minimum_depth,excavation,select,EngineeringError
from .geometry import alignment
STAGES=['Input inventory','Drawing inspection','Coordinate validation','Data extraction','Plot and corner matching','Input validation','Engineering calculations','Schedule validation','Excel export','Output verification']
log=logging.getLogger(__name__)
def issue(results,category,description,source_file=None,source_entity=None,plot_id=None,corner=None,severity='error',action='Provide confirmed engineering inputs and reprocess.'):
 results['issues'].append({'id':f"ISS-{len(results['issues'])+1:05}",'severity':severity,'category':category,'description':description,'source_file':source_file,'source_entity':source_entity,'plot_id':plot_id,'corner':corner,'impact':'Results cannot be treated as a verified complete schedule' if severity=='error' else 'Review supporting evidence','next_action':action})
def persist(project_id,results,stage_index,status='completed',message=None):
 with storage.LOCK:
  p=storage.load(project_id);p['results']=results
  p['job']['stages'][stage_index].update(status=status,message=message,updated_at=storage.now())
  p['job']['current_stage']=STAGES[stage_index];storage.save(p)
def files_for_run(p,work,results):
 inputs=[]
 for f in p['files']:
  original=storage.directory(p['id'])/'sources'/f['stored_name']
  if f['extension']=='.zip':
   for index,i in enumerate(archive_members(original)):
    if Path(i.filename).suffix.lower()=='.zip':issue(results,'archive','Nested archive was not expanded; upload its supported drawing files separately.',f['name']+'::'+i.filename,severity='warning')
    if i.is_dir() or Path(i.filename).suffix.lower() not in ('.dxf','.xlsx','.json','.pdf','.dwg'):continue
    dest=work/f"{f['id']}-{index}{Path(i.filename).suffix.lower()}"
    with zipfile.ZipFile(original) as z,z.open(i) as src,dest.open('wb') as dst:shutil.copyfileobj(src,dst,1024*1024)
    inputs.append({'path':dest,'source':f['name']+'::'+i.filename,'category':f['category'],'extension':dest.suffix,'file_id':f['id']})
  else:inputs.append({'path':original,'source':f['name'],'category':f['category'],'extension':f['extension'],'file_id':f['id']})
 return inputs

def reviewed_calculations(manifest,results,drawings):
 from .models import ReviewedInputs
 m=ReviewedInputs.model_validate(manifest)
 results['dataset_kind']=m.dataset_kind;results['review']={'reviewer':m.reviewer,'reason':m.review_reason,'time':storage.now()}
 available={d['source_file']:d for d in drawings};accepted=[]
 handles={d['source_file']:{handle for r in d['records'] for handle in [r['source_entity']]+[a['source_entity'] for a in r.get('attributes',[])]} for d in drawings}
 for a in m.alignments:
  decision=alignment([r.model_dump() for r in a.references],a.tolerance_m,a.justification)
  decision.update(source_file=a.source_file,target_file=a.target_file,original_units={k:available.get(k,{}).get('units_code') for k in (a.source_file,a.target_file)})
  results['coordinates'].append(decision)
  if a.source_file not in available or a.target_file not in available:
   decision['status']='blocked';decision['reason']='Alignment references a drawing not available in this project'
  if decision['status']=='validated':accepted.append({a.source_file,a.target_file})
  else:issue(results,'coordinates','Reviewed coordinate transformation failed validation',a.source_file)
 for plot in m.plots:
  plot_data=plot.model_dump();plot_data['status']='engineer_reviewed_import';results['plots'].append(plot_data)
  for c in plot.corners:
   candidates=[];errors=[];refs=c.sources+[r for constraint in c.constraints for r in constraint.sources]
   used={r.file for r in refs}
   for ref in refs:
    if ref.file not in available:errors.append(f'Source drawing not uploaded: {ref.file}')
    elif ref.entity not in handles[ref.file]:errors.append(f'Source entity not available in extracted evidence: {ref.file} / {ref.entity}')
   if len(used)>1:
    connected={next(iter(used))}
    for _ in range(len(available)+1):
     for pair in accepted:
      if pair&connected:connected|=pair
    if not used<=connected:errors.append('Cross-drawing source references lack a validated connected alignment')
   for constraint in c.constraints:
    if constraint.applicability=='unknown':errors.append(f'{constraint.reason}: applicability unresolved');continue
    if constraint.applicability=='inapplicable':continue
    try:
     if constraint.reason=='Min Depth':
      if constraint.minimum_depth_m is None:raise EngineeringError('An explicitly reviewed minimum depth is required')
      candidate=minimum_depth(c.ground_level_m,constraint.minimum_depth_m)
     elif constraint.reason in ('Pipe','Manhole'):
      candidate=excavation(constraint.invert_m,constraint.centre_distance_m,constraint.diameter_m,constraint.reason,constraint.competent_strata is True)
     else:
      if constraint.level_m is None:raise EngineeringError('Engineer-reviewed candidate level is required; automatic tree/geology/WPL rules are not implemented')
      candidate={'reason':constraint.reason,'level':str(constraint.level_m),'steps':['Candidate elevation explicitly supplied by reviewer; not derived automatically'],'inputs':{'reviewed_level_m':constraint.level_m},'source_rule':'Engineer-reviewed input'}
     candidate.update(sources=[s.model_dump() for s in constraint.sources],reviewer_explanation=constraint.explanation)
     candidates.append(candidate)
     for warning in candidate.get('warnings',[]):issue(results,'calculation',warning,plot_id=plot.plot_id,corner=c.corner,severity='warning')
    except EngineeringError as e:errors.append(str(e))
   result={'id':f'{plot.plot_id}-{c.corner}','plot_id':plot.plot_id,'corner':c.corner,'point':c.point,'ground_level':c.ground_level_m,'sources':[r.model_dump() for r in refs],'review_status':'synthetic_test' if m.dataset_kind=='synthetic_test' else 'engineer_reviewed_import'}
   if errors or not candidates:
    result.update(status='blocked',bearing_level=None,reason=None,candidates=candidates,unresolved_inputs=errors or ['No applicable constraints'])
    for error in errors or ['No applicable constraints']:issue(results,'inputs',error,plot_id=plot.plot_id,corner=c.corner)
   else:result.update(select(candidates))
   results['calculations'].append(result)

def run(project_id):
 results={'status':'processing','drawings':[],'extraction':[],'coordinates':[],'plots':[],'calculations':[],'issues':[],'matches':[],'summary':{},'template':None,'dataset_kind':'drawing_extraction'}
 stage=0
 try:
  p=storage.load(project_id);work=storage.directory(project_id)/'runs'/p['job']['id'];work.mkdir(parents=True,exist_ok=True)
  with storage.LOCK:
   p['job']['status']='running';storage.save(p)
  for stage,name in enumerate(STAGES):
   persist(project_id,results,stage,'running')
   if stage==0:
    inputs=files_for_run(p,work,results)
    if not inputs:issue(results,'files','No supported inputs supplied')
   elif stage==1:
    from .cad import inspect
    for f in inputs:
     if f['extension']=='.dxf':
      try:
       drawing=inspect(f['path'],f['source']);results['drawings'].append(drawing)
       if drawing.get('invalid_geometry_count'):issue(results,'geometry','Drawing contains nonfinite geometry; affected entities were rejected',f['source'])
       if drawing['units_code']==0:issue(results,'units','Drawing units are unspecified',f['source'])
       if drawing['truncated']:issue(results,'cad','Extracted records reached safety cap; source evidence is incomplete',f['source'])
       for block in drawing['blocks']:
        if block['xref']:issue(results,'xref',f"External reference requires explicit placement/units validation: {block['xref']}",f['source'],severity='warning')
       if drawing['unsupported_entities']:issue(results,'cad',f"Uninterpreted entity types: {drawing['unsupported_entities']}",f['source'],severity='warning')
      except Exception:log.exception('CAD parse failed');issue(results,'cad','DXF could not be parsed. Check the conversion and source file.',f['source'])
     elif f['extension']=='.dwg':issue(results,'format','DWG is preserved as reference only. Supply a DXF export; no DWG converter is bundled.',f['source'],severity='warning')
     elif f['extension']=='.pdf':issue(results,'format','PDF is preserved as reference only; automatic PDF geometry interpretation is not implemented.',f['source'],severity='warning')
   elif stage==2:
    for d in results['drawings']:
     results['coordinates'].append({'source_file':d['source_file'],'original_units':d['units_code'],'status':'unvalidated','candidate_reference_points':0,'validated_reference_points':0,'transformation':None,'reason':'No independent shared control points have been confirmed. Similar coordinates or unit metadata alone do not establish alignment.'})
   elif stage==3:
    for d in results['drawings']:
     remaining=max(0,150000-len(results['extraction']));results['extraction'].extend(d['records'][:remaining])
     if len(d['records'])>remaining:issue(results,'cad','Combined evidence display is capped at 150,000 records; evidence is incomplete.',d['source_file'])
   elif stage==4:
    for r in results['extraction']:
     if r['layer'].lower()=='plot number' and r.get('text'):
      plot_id=r['text'].strip()
      existing=next((x for x in results['plots'] if x['plot_id']==plot_id),None)
      if existing:issue(results,'plots','Duplicate plot label',r['source_file'],r['source_entity'],plot_id=plot_id)
      else:results['plots'].append({'plot_id':plot_id,'corners':[],'status':'label_only_requires_review','sources':[{'file':r['source_file'],'entity':r['source_entity']}]})
    if results['plots']:issue(results,'corners','Plot labels extracted, but numbered markers still require physical corner and plot association. No corner positions assumed.')
   elif stage==5:
    manifests=[f for f in inputs if f['extension']=='.json']
    direct_manifests=[f for f in manifests if '::' not in f['source']]
    if len(direct_manifests)==1 and len(manifests)>1:
     issue(results,'inputs','A standalone reviewed-input revision supersedes JSON packaged inside archives.',severity='info')
     manifests=direct_manifests
    if len(manifests)>1:issue(results,'inputs','Multiple reviewed-input manifests are ambiguous; retain exactly one')
    elif manifests:
     try:
      # Label-only records remain in raw extraction, replaced by explicit reviewed plots.
      from .models import ReviewedInputs
      manifest=ReviewedInputs.model_validate(json.loads(manifests[0]['path'].read_text())).model_dump()
     except Exception:log.exception('Reviewed input invalid');issue(results,'inputs','Reviewed-input JSON failed schema or evidence validation. See docs/data_dictionary.md.')
    else:
     issue(results,'inputs','No reviewed corner/constraint inputs supplied. Automatic semantic association is incomplete; engineering calculations are blocked.')
    templates=[f for f in inputs if f['extension']=='.xlsx']
    if len(templates)==1:
     from .excel import inspect_template
     try:results['template']=inspect_template(templates[0]['path'])
     except Exception:log.exception('Template validation failed');issue(results,'excel','Workbook unreadable or confirmed mapping has changed',templates[0]['source'])
    else:issue(results,'excel','Exactly one existing Excel template is required')
   elif stage==6:
    if 'manifest' in locals():
     results['plots']=[];reviewed_calculations(manifest,results,results['drawings'])
    if not results['calculations']:persist(project_id,results,stage,'blocked','No validated corner inputs');continue
   elif stage==7:
    issue(results,'schedule','Complete schedule export is blocked: workbook engineering dependency mapping, dynamic corner association and all applicable site constraints need confirmation. A draft schedule may contain reviewed candidate results; it is not a complete construction schedule.',action='Confirm remaining workbook inputs and engineering branches with the client.')
   elif stage==8:
    if not results['template']:persist(project_id,results,stage,'blocked','No validated template');continue
    from .excel import export_review,export_draft
    draft=bool(results['calculations'])
    target=work/('foundation-draft-schedule.xlsx' if draft else 'foundation-review-only.xlsx')
    results['status']='requires_review'
    metadata=(export_draft if draft else export_review)(templates[0]['path'],target,results)
    with storage.LOCK:
     current=storage.load(project_id);current['outputs'].append({'id':storage.uid(),'path':str(target.relative_to(storage.directory(project_id))),**metadata});storage.save(current)
   elif stage==9:
    results['summary']={'source_files':len(p['files']),'drawings':len(results['drawings']),'extracted_records':len(results['extraction']),'plots':len(results['plots']),'expected_corners':4*len(results['plots']),'corners_calculated':sum(r['status']=='calculated' for r in results['calculations']),'corners_requiring_review':4*len(results['plots']),'blocking_errors':sum(i['severity']=='error' for i in results['issues']),'warnings':sum(i['severity']=='warning' for i in results['issues']),'schedule_complete':False}
   persist(project_id,results,stage)
  results['status']='requires_review'
  report=work/'validation-report.json';report.write_text(json.dumps(results,indent=2,allow_nan=False))
  with storage.LOCK:
   current=storage.load(project_id);current['results']=results;current['status']='requires_review';current['job']['status']='completed_with_issues';current['job']['finished_at']=storage.now()
   for f in current['files']:
    related=[i for i in results['issues'] if i.get('source_file') and (i['source_file']==f['name'] or i['source_file'].startswith(f['name']+'::'))]
    f['processing_status']='reference_only' if f['extension'] in ('.pdf','.dwg') else 'failed' if any(i['severity']=='error' for i in related) else 'processed_with_warnings' if related else 'processed' if any(d['source_file']==f['name'] or d['source_file'].startswith(f['name']+'::') for d in results['drawings']) or f['extension'] in ('.xlsx','.json') else 'reference_only'
   current['outputs'].append({'id':storage.uid(),'path':str(report.relative_to(storage.directory(project_id))),'name':report.name,'kind':'validation_report','verified':True,'schedule_complete':False});storage.audit(current,'processing_completed',job_id=current['job']['id']);storage.save(current)
 except Exception:
  log.exception('Processing failed')
  issue(results,'processing','Processing stopped unexpectedly. Source files are preserved; inspect backend logs and retry.',action='Check dependencies, file readability and local resources, then retry.')
  results['status']='failed'
  with storage.LOCK:
   p=storage.load(project_id);p['results']=results;p['status']='failed';p['job']['status']='failed';p['job']['error']='Processing failed. Source files are preserved.';p['job']['stages'][stage]['status']='failed'
   for f in p['files']:f['processing_status']='failed'
   storage.audit(p,'processing_failed');storage.save(p)
