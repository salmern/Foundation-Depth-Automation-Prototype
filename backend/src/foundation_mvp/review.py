"""Immutable, auditable revisions of explicitly reviewed calculation inputs."""
import json
from . import storage

def current_inputs(project):
    files=[f for f in project['files'] if f['extension']=='.json']
    if len(files)>1:raise ValueError('Multiple active reviewed input documents; remove obsolete revisions first')
    if not files:return {'inputs':None,'revision':None}
    f=files[0]
    path=storage.directory(project['id'])/'sources'/f['stored_name']
    return {'inputs':json.loads(path.read_text()),'revision':f['id']}

def save_revision(project,inputs,change_reason):
    reason=change_reason.strip()
    if len(reason)<3:raise ValueError('Explain the change using at least three characters')
    if not inputs['reviewer'].strip() or not inputs['review_reason'].strip():raise ValueError('Reviewer and review reason cannot be blank')
    encoded=json.dumps(inputs,indent=2,allow_nan=False).encode()
    if len(encoded)>10*1024*1024:raise ValueError('Reviewed input document exceeds 10 MiB')
    directory=storage.directory(project['id'])/'sources';directory.mkdir(exist_ok=True)
    old=[f for f in project['files'] if f['extension']=='.json']
    retained=[f for f in project['files'] if f['extension']!='.json']
    if len(retained)>=60 or sum(p.stat().st_size for p in directory.iterdir() if p.is_file())+len(encoded)>2*1024**3:
        raise ValueError('Project source storage limit reached')
    file_id=storage.uid();path=directory/(file_id+'.json');path.write_bytes(encoded)
    record={'id':file_id,'name':f'reviewed-inputs-{file_id[:8]}.json','stored_name':path.name,
            'extension':'.json','size':len(encoded),'category':'reviewed_inputs','sha256':storage.digest(path),
            'uploaded_at':storage.now(),'upload_status':'uploaded','validation_status':'schema_validated',
            'processing_status':'not_started'}
    project['files']=retained+[record]
    project.update(results=None,outputs=[],job=None,status='not_started')
    storage.audit(project,'reviewed_inputs_revised',reviewer=inputs['reviewer'],reason=reason,
                  previous_revisions=[{'id':f['id'],'sha256':f['sha256']} for f in old],
                  revised_file_id=file_id,revised_sha256=record['sha256'],
                  value_storage='Original and revised input values retained in immutable source files')
    storage.save(project)
    return {'revision':file_id,'inputs':inputs,'message':'Reviewed inputs saved. Start processing again to recalculate.'}
