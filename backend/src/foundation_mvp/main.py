from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
import logging,os,zipfile
from pathlib import Path
from typing import Literal
from fastapi import FastAPI,File,Form,HTTPException,Query,UploadFile,Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse,JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from . import storage
from .models import ProjectCreate,Envelope,ApiResponse,ProjectView,FileView,JobView,IssueView,ExtractionView,ErrorResponse,ReviewRevision
from .safety import filename,archive_members,MAX_FILE,InputError
from .pipeline import run,STAGES
from .engineering import brief_example
pool:ThreadPoolExecutor|None=None
@asynccontextmanager
async def lifespan(app):
 global pool
 storage.recover();pool=ThreadPoolExecutor(max_workers=1,thread_name_prefix='foundation-processing')
 try:yield
 finally:
  pool.shutdown(wait=True);pool=None
app=FastAPI(title='Foundation Depth Automation',version='0.1.0',lifespan=lifespan,responses={404:{'model':ErrorResponse},409:{'model':ErrorResponse},413:{'model':ErrorResponse},422:{'model':ErrorResponse},500:{'model':ErrorResponse}},description='Local engineering review MVP. Complete construction schedule export is blocked pending confirmed source mapping. All levels in metres.')
app.add_middleware(CORSMiddleware,allow_origins=os.environ.get('FOUNDATION_CORS_ORIGINS','http://localhost:3000,http://127.0.0.1:3000').split(','),allow_methods=['GET','POST','DELETE'],allow_headers=['Content-Type'])
@app.exception_handler(HTTPException)
async def http_error(request,exc):return JSONResponse(status_code=exc.status_code,content={'error':{'code':str(exc.status_code),'message':exc.detail}})
@app.exception_handler(RequestValidationError)
async def validation_error(request,exc):return JSONResponse(status_code=422,content={'error':{'code':'validation_error','message':'Request validation failed','details':[{'field':'.'.join(map(str,e['loc'])),'message':e['msg']} for e in exc.errors()]}})
@app.exception_handler(Exception)
async def unexpected(request,exc):
 logging.exception('Unhandled API error',exc_info=exc)
 return JSONResponse(status_code=500,content={'error':{'code':'internal_error','message':'The request could not be completed. Check the backend logs.'}})
def get(project_id):
 try:return storage.load(project_id)
 except ValueError:raise HTTPException(422,'Invalid project identifier') from None
 except FileNotFoundError:raise HTTPException(404,'Project not found') from None

def public(p):
 return {k:v for k,v in p.items() if k not in ('results','files','outputs')}|{'files':[{k:v for k,v in f.items() if k!='stored_name'} for f in p['files']],'outputs':[{k:v for k,v in o.items() if k!='path'} for o in p['outputs']],'summary':(p.get('results') or {}).get('summary',{})}
def idle(p):
 if p.get('job') and p['job']['status'] in ('queued','running'):raise HTTPException(409,'Processing is active; wait before changing files or starting another run')
def invalidate(p):p.update(results=None,outputs=[],job=None,status='not_started')
def result(p):
 if p.get('results') is None:raise HTTPException(409,'No processing results yet')
 return p['results']
@app.get('/api/health',response_model=Envelope)
def health():return {'data':{'status':'ok','persistence':'local_files','schedule_export':'blocked_pending_confirmed_mapping'}}
@app.post('/api/projects',status_code=201,response_model=ApiResponse[ProjectView])
def create_project(body:ProjectCreate):return {'data':public(storage.create(body.name))}
@app.get('/api/projects',response_model=ApiResponse[list[ProjectView]])
def projects():return {'data':[public(p) for p in storage.list_projects()]}
@app.get('/api/projects/{project_id}',response_model=ApiResponse[ProjectView])
def project(project_id:str):return {'data':public(get(project_id))}
@app.get('/api/examples/brief',response_model=Envelope)
def example():return {'data':brief_example()}
@app.post('/api/projects/{project_id}/files',status_code=201,response_model=ApiResponse[FileView])
async def upload(project_id:str,file:UploadFile=File(...),category:Literal['foundation','topography','drainage','trees','reference','template','reviewed_inputs']=Form(...)):
 p=get(project_id);idle(p)
 try:ext=filename(file.filename)
 except InputError as e:raise HTTPException(422,str(e)) from None
 if category=='template' and ext!='.xlsx':raise HTTPException(422,'Excel template purpose requires an XLSX file')
 if (category=='reviewed_inputs') != (ext=='.json'):raise HTTPException(422,'Reviewed inputs must be JSON and use the reviewed_inputs purpose')
 file_id=storage.uid();folder=storage.directory(project_id)/'sources';folder.mkdir(exist_ok=True);path=folder/(file_id+ext);size=0
 try:
  with path.open('xb') as dst:
   while chunk:=await file.read(1024*1024):
    size+=len(chunk)
    if size>MAX_FILE:raise HTTPException(413,'File exceeds 600 MiB upload limit')
    dst.write(chunk)
  if size==0:raise HTTPException(422,'File is empty')
  if ext in ('.zip','.xlsx'):
   members=archive_members(path)
   if ext=='.xlsx' and (size>25*1024**2 or sum(i.file_size for i in members)>128*1024**2):raise InputError('Workbook exceeds 25 MiB compressed / 128 MiB expanded safety limit')
  with path.open('rb') as stream:head=stream.read(65536)
  if ext=='.dwg' and not head.startswith(b'AC10'):raise InputError('File does not have a supported DWG signature')
  if ext=='.pdf' and not head.startswith(b'%PDF'):raise InputError('File does not have a PDF signature')
  if ext=='.dxf' and b'SECTION' not in head and not head.startswith(b'AutoCAD Binary DXF'):raise InputError('File is not a recognised DXF container')
  if ext=='.json':
   import json
   from .models import ReviewedInputs
   if size>10*1024*1024:raise InputError('Reviewed input JSON exceeds 10 MiB')
   try:ReviewedInputs.model_validate(json.loads(path.read_text()))
   except Exception:raise InputError('Reviewed-input JSON is invalid; consult docs/data_dictionary.md') from None
  sha=storage.digest(path)
  with storage.LOCK:
   p=get(project_id);idle(p)
   if len(p['files'])>=60 or sum(x.stat().st_size for x in folder.iterdir() if x.is_file())>2*1024**3:raise HTTPException(413,'Project input limit is 60 files / 2 GiB')
   if any(f['sha256']==sha for f in p['files']):raise HTTPException(409,'Identical file already uploaded')
   if any(f['name'].casefold()==file.filename.casefold() for f in p['files']):raise HTTPException(409,'File name already exists. Remove the previous revision before replacement.')
   record={'id':file_id,'name':file.filename,'stored_name':path.name,'extension':ext,'size':size,'category':category,'sha256':sha,'uploaded_at':storage.now(),'upload_status':'uploaded','validation_status':'container_validated','processing_status':'not_started'}
   p['files'].append(record);invalidate(p);storage.audit(p,'file_uploaded',file_id=file_id,name=file.filename,sha256=sha,category=category);storage.save(p)
  return {'data':{k:v for k,v in record.items() if k!='stored_name'}}
 except InputError as e:
  path.unlink(missing_ok=True);raise HTTPException(422,str(e)) from None
 except Exception:
  path.unlink(missing_ok=True);raise
 finally:await file.close()
@app.delete('/api/projects/{project_id}/files/{file_id}',response_model=Envelope)
def delete_file(project_id:str,file_id:str):
 with storage.LOCK:
  p=get(project_id);idle(p);f=next((f for f in p['files'] if f['id']==file_id),None)
  if not f:raise HTTPException(404,'File not found')
  # Keep source bytes for provenance, hide from active project inputs.
  p['files'].remove(f);invalidate(p);storage.audit(p,'file_removed',file_id=file_id,name=f['name']);storage.save(p)
 return {'data':{'removed':True,'source_preserved':True}}
@app.post('/api/projects/{project_id}/process',status_code=202,response_model=ApiResponse[JobView])
def process(project_id:str):
 with storage.LOCK:
  p=get(project_id);idle(p)
  if pool is None:raise HTTPException(503,'Processing service is not ready')
  if not p['files']:raise HTTPException(422,'Upload source files before processing')
  if any(x['job'] and x['job']['status'] in ('queued','running') for x in storage.list_projects()):raise HTTPException(409,'Another project is processing. Local MVP runs one job at a time.')
  job={'id':storage.uid(),'status':'queued','started_at':storage.now(),'current_stage':None,'stages':[{'name':s,'status':'pending'} for s in STAGES]}
  p.update(job=job,status='processing',results=None,outputs=[])
  for f in p['files']:f['processing_status']='queued'
  storage.audit(p,'processing_started',job_id=job['id']);storage.save(p);pool.submit(run,project_id)
 return {'data':job}
@app.get('/api/projects/{project_id}/jobs/{job_id}',response_model=ApiResponse[JobView])
def job(project_id:str,job_id:str):
 p=get(project_id)
 if not p.get('job') or p['job']['id']!=job_id:raise HTTPException(404,'Job not found')
 return {'data':p['job']}
@app.get('/api/projects/{project_id}/extraction',response_model=ApiResponse[ExtractionView])
def extraction(project_id:str,q:str=Query('',max_length=200),offset:int=Query(0,ge=0),limit:int=Query(100,ge=1,le=500)):
 rows=result(get(project_id))['extraction'];filtered=[r for r in rows if q.casefold() in str(r).casefold()]
 return {'data':{'records':filtered[offset:offset+limit],'total':len(filtered),'offset':offset,'limit':limit}}
@app.get('/api/projects/{project_id}/coordinates',response_model=Envelope)
def coordinates(project_id:str):return {'data':result(get(project_id))['coordinates']}
@app.get('/api/projects/{project_id}/plots',response_model=Envelope)
def plots(project_id:str):return {'data':result(get(project_id))['plots']}
@app.get('/api/projects/{project_id}/calculations',response_model=Envelope)
def calculations(project_id:str):return {'data':result(get(project_id))['calculations']}
@app.get('/api/projects/{project_id}/calculations/{result_id}',response_model=Envelope)
def calculation(project_id:str,result_id:str):
 found=next((r for r in result(get(project_id))['calculations'] if r['id']==result_id),None)
 if found is None:raise HTTPException(404,'Calculation not found')
 return {'data':found}
@app.get('/api/projects/{project_id}/issues',response_model=ApiResponse[list[IssueView]])
def issues(project_id:str,severity:Literal['error','warning','info']|None=None,plot:str|None=Query(None,max_length=40),category:str|None=Query(None,max_length=100),source:str|None=Query(None,max_length=500)):
 rows=result(get(project_id))['issues']
 return {'data':[r for r in rows if (not severity or r['severity']==severity) and (not plot or r['plot_id']==plot) and (not category or r['category']==category) and (not source or r['source_file']==source)]}
@app.get('/api/projects/{project_id}/reviewed-inputs',response_model=Envelope)
def reviewed_inputs(project_id:str):
 from .review import current_inputs
 try:return {'data':current_inputs(get(project_id))}
 except ValueError as e:raise HTTPException(409,str(e)) from None
@app.post('/api/projects/{project_id}/reviewed-inputs',response_model=Envelope)
def revise_inputs(project_id:str,body:ReviewRevision):
 from .review import save_revision
 with storage.LOCK:
  p=get(project_id);idle(p)
  try:return {'data':save_revision(p,body.inputs.model_dump(),body.change_reason)}
  except ValueError as e:raise HTTPException(422,str(e)) from None
@app.post('/api/projects/{project_id}/export',response_model=Envelope)
def export(project_id:str):
 p=get(project_id);idle(p)
 available=next((o for o in p['outputs'] if o['kind']=='draft_schedule'),None)
 if available:
  return {'data':{k:v for k,v in available.items() if k!='path'}}
 raise HTTPException(409,'No populated draft schedule is available. Process reviewed corner inputs with a valid template first. A final construction schedule remains blocked pending full engineering confirmation.')
@app.get('/api/projects/{project_id}/outputs/{output_id}')
def download(project_id:str,output_id:str):
 p=get(project_id);o=next((o for o in p['outputs'] if o['id']==output_id),None)
 if not o:raise HTTPException(404,'Output not found')
 base=storage.directory(project_id);path=(base/o['path']).resolve()
 if not path.is_relative_to(base.resolve()) or not path.is_file():raise HTTPException(404,'Output file unavailable')
 return FileResponse(path,filename=o['name'],media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if path.suffix=='.xlsx' else 'application/json')
