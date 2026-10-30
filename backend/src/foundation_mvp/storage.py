"""Atomic local persistence; immutable uploads and serialised project mutations."""
import hashlib,json,os,re,threading,uuid
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(os.environ.get('FOUNDATION_DATA_DIR',Path(__file__).resolve().parents[3]/'data'/'working')).resolve()
LOCK=threading.RLock()
def now(): return datetime.now(timezone.utc).isoformat()
def uid(): return uuid.uuid4().hex
def valid_id(value):
 if not re.fullmatch('[a-f0-9]{32}',value): raise ValueError('Invalid identifier')
 return value
def directory(project_id): return ROOT/valid_id(project_id)
def load(project_id):
 p=directory(project_id)/'project.json'
 if not p.exists(): raise FileNotFoundError('Project not found')
 return json.loads(p.read_text())
def save(project):
 folder=directory(project['id']);folder.mkdir(parents=True,exist_ok=True)
 temp=folder/'project.tmp';temp.write_text(json.dumps(project,indent=2,allow_nan=False));temp.replace(folder/'project.json')
def create(name):
 name=name.strip()
 if not 1<=len(name)<=120 or any(ord(x)<32 for x in name): raise ValueError('Project name must contain 1–120 printable characters')
 with LOCK:
  p={'id':uid(),'name':name,'created_at':now(),'status':'not_started','files':[],'job':None,'results':None,'outputs':[],'audit':[]};save(p);return p

def list_projects():
 ROOT.mkdir(parents=True,exist_ok=True)
 return [load(p.parent.name) for p in sorted(ROOT.glob('*/project.json'))]
def audit(p,action,**details): p['audit'].append({'time':now(),'action':action,**details})
def digest(path):
 with path.open('rb') as s:return hashlib.file_digest(s,'sha256').hexdigest()
def recover():
 with LOCK:
  for p in list_projects():
   if p.get('job') and p['job']['status'] in ('queued','running'):
    p['job']['status']='interrupted';p['job']['error']='Server restarted during processing. Start a new run.';p['status']='interrupted'
    for stage in p['job'].get('stages',[]):
     if stage['status']=='running':stage['status']='interrupted'
    for f in p['files']:
     if f['processing_status'] in ('queued','processing'):f['processing_status']='interrupted'
    audit(p,'job_interrupted');save(p)
