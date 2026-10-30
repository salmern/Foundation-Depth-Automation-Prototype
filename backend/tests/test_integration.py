"""Real library and API integration tests. Skipped only when dependencies absent."""
import importlib.util,json,sys,tempfile,time,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
FIXTURES=Path(__file__).parent/'fixtures'
TEMPLATE=Path(__file__).resolve().parents[3]/'2 Template/MASTER Foundation Schedule.xlsx'
DEPS=all(importlib.util.find_spec(n) for n in ('fastapi','ezdxf','openpyxl','shapely','httpx'))
@unittest.skipUnless(DEPS,'Install backend requirements to execute real CAD/Excel/API tests')
class LibraryTests(unittest.TestCase):
 def test_cad_source_handles(self):
  from foundation_mvp.cad import inspect
  d=inspect(FIXTURES/'synthetic-house.dxf','synthetic-house.dxf')
  self.assertEqual(d['units_code'],6);self.assertEqual(d['entity_counts']['POINT'],4);self.assertEqual(d['entity_counts']['LINE'],1)
  self.assertEqual({r['source_entity'] for r in d['records']},{'A1','A2','A3','A4','B1'})
 def test_invalid_polygon(self):
  from foundation_mvp.geometry import polygon_corners
  with self.assertRaises(ValueError):polygon_corners([(0,0),(1,1),(0,1),(1,0)])
 def test_manifest_schema(self):
  from foundation_mvp.models import ReviewedInputs
  m=json.loads((FIXTURES/'synthetic-reviewed-inputs.json').read_text());ReviewedInputs.model_validate(m)
  m['plots'][0]['corners'][1]['corner']=1
  with self.assertRaises(ValueError):ReviewedInputs.model_validate(m)
  m=json.loads((FIXTURES/'synthetic-reviewed-inputs.json').read_text());m['plots'][0]['corners'][0]['ground_level_m']=True
  with self.assertRaises(ValueError):ReviewedInputs.model_validate(m)
  m=json.loads((FIXTURES/'synthetic-reviewed-inputs.json').read_text());m['plots'][0]['corners'][0]['corner']=True
  with self.assertRaises(ValueError):ReviewedInputs.model_validate(m)
 def test_actual_workbook_mapping_and_export(self):
  from foundation_mvp.excel import inspect_template,export_review
  from openpyxl import load_workbook
  info=inspect_template(TEMPLATE);self.assertEqual(info['mapping']['bearing_level'],['U','V','W','X'])
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'review.xlsx';export_review(TEMPLATE,p,{'status':'requires_review','issues':[],'calculations':[]})
   wb=load_workbook(p);self.assertIn('Automation Review',wb.sheetnames);self.assertEqual(wb['Generic 4 corner output']['U10'].value,'=Input!JP10');wb.close()
 def test_actual_template_draft_export(self):
  from foundation_mvp.excel import export_draft
  from foundation_mvp.engineering import minimum_depth,excavation,select
  from openpyxl import load_workbook
  manifest=json.loads((FIXTURES/'synthetic-reviewed-inputs.json').read_text());plot=manifest['plots'][0];results={'status':'requires_review','issues':[],'plots':[plot],'calculations':[]}
  for c in plot['corners']:
   candidates=[minimum_depth(c['ground_level_m'])]
   if c['corner']==1:candidates.append(excavation(98.2,.6,.1,competent=True))
   results['calculations'].append({'plot_id':plot['plot_id'],'corner':c['corner'],**select(candidates)})
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'draft.xlsx';meta=export_draft(TEMPLATE,p,results);self.assertFalse(meta['schedule_complete'])
   w=load_workbook(p);self.assertEqual(w['Generic 4 corner output']['U10'].value,97.95);self.assertEqual(w['Generic 4 corner output']['I10'].value,'Pipe');self.assertTrue(w['Generic 4 corner output'].row_dimensions[11].hidden);w.close()
 def test_changed_template_rejected(self):
  from foundation_mvp.excel import inspect_template
  from openpyxl import load_workbook
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'changed.xlsx';w=load_workbook(TEMPLATE);w['Generic 4 corner output']['I8']='Changed';w.save(p);w.close()
   with self.assertRaises(ValueError):inspect_template(p)
@unittest.skipUnless(DEPS,'Install backend requirements to execute API workflow')
class ApiTests(unittest.TestCase):
 def setUp(self):
  from foundation_mvp import storage
  from foundation_mvp.main import app
  from fastapi.testclient import TestClient
  self.storage=storage;self.old=storage.ROOT;self.tmp=tempfile.TemporaryDirectory();storage.ROOT=Path(self.tmp.name);self.client=TestClient(app);self.client.__enter__()
 def tearDown(self):self.client.__exit__(None,None,None);self.storage.ROOT=self.old;self.tmp.cleanup()
 def create(self):
  response=self.client.post('/api/projects',json={'name':'Integration test'});self.assertEqual(response.status_code,201);return response.json()['data']['id']
 def upload(self,p,path,category):
  with path.open('rb') as f:return self.client.post(f'/api/projects/{p}/files',files={'file':(path.name,f)},data={'category':category})
 def wait(self,p,job):
  deadline=time.monotonic()+60
  while time.monotonic()<deadline:
   r=self.client.get(f'/api/projects/{p}/jobs/{job}').json()['data']
   if r['status'] not in ('queued','running'):return r
   time.sleep(.05)
  self.fail('Job did not finish within 60 seconds')
 def test_validation_and_not_found(self):
  self.assertEqual(self.client.post('/api/projects',json={'name':'  '}).status_code,422)
  self.assertEqual(self.client.get('/api/projects/not-an-id').status_code,422)
  self.assertEqual(self.client.get('/api/projects/'+'f'*32).status_code,404)
  p=self.create();self.assertEqual(self.client.post(f'/api/projects/{p}/process').status_code,422)
  self.assertEqual(self.client.get(f'/api/projects/{p}/calculations').status_code,409)
 def test_upload_guards(self):
  p=self.create()
  for name,data in [('empty.dxf',b''),('../bad.dxf',b'a'),('x.exe',b'a'),('bad.xlsx',b'bad')]:
   self.assertEqual(self.client.post(f'/api/projects/{p}/files',files={'file':(name,data)},data={'category':'foundation'}).status_code,422)
  self.assertEqual(self.upload(p,FIXTURES/'synthetic-house.dxf','foundation').status_code,201)
  self.assertEqual(self.upload(p,FIXTURES/'synthetic-house.dxf','foundation').status_code,409)
 def test_real_processing_and_download(self):
  p=self.create()
  for path,category in [(FIXTURES/'synthetic-house.dxf','foundation'),(FIXTURES/'synthetic-reviewed-inputs.json','reviewed_inputs'),(TEMPLATE,'template')]:self.assertEqual(self.upload(p,path,category).status_code,201)
  r=self.client.post(f'/api/projects/{p}/process');self.assertEqual(r.status_code,202);job=r.json()['data']['id'];done=self.wait(p,job)
  self.assertEqual(done['status'],'completed_with_issues')
  extraction=self.client.get(f'/api/projects/{p}/extraction').json()['data'];self.assertEqual(extraction['total'],5)
  calculations=self.client.get(f'/api/projects/{p}/calculations').json()['data'];self.assertEqual(len(calculations),4);self.assertEqual(calculations[0]['bearing_level'],97.95);self.assertEqual(calculations[0]['reason'],'Pipe')
  detail=self.client.get(f'/api/projects/{p}/calculations/TEST-R2G-1');self.assertEqual(detail.status_code,200)
  self.assertTrue(self.client.get(f'/api/projects/{p}/issues?severity=error').json()['data'])
  self.assertEqual(self.client.post(f'/api/projects/{p}/export').json()['data']['kind'],'draft_schedule')
  outputs=self.client.get(f'/api/projects/{p}').json()['data']['outputs'];self.assertEqual(len(outputs),2)
  out=next(o for o in outputs if o['kind']=='draft_schedule');binary=self.client.get(f"/api/projects/{p}/outputs/{out['id']}");self.assertEqual(binary.status_code,200)
  from openpyxl import load_workbook
  import io
  w=load_workbook(io.BytesIO(binary.content));self.assertIn('Automation Review',w.sheetnames);self.assertEqual(w['Generic 4 corner output']['U10'].value,97.95);self.assertEqual(w['Generic 4 corner output']['I10'].value,'Pipe');self.assertEqual(w['Generic 4 corner output']['U11'].value,'=Input!JP11');w.close()
 def test_audited_review_revision(self):
  p=self.create();m=json.loads((FIXTURES/'synthetic-reviewed-inputs.json').read_text())
  r=self.client.post(f'/api/projects/{p}/reviewed-inputs',json={'inputs':m,'change_reason':'Initial synthetic review'});self.assertEqual(r.status_code,200)
  loaded=self.client.get(f'/api/projects/{p}/reviewed-inputs').json()['data'];self.assertEqual(loaded['inputs']['reviewer'],m['reviewer'])
  self.assertEqual(self.client.get(f'/api/projects/{p}').json()['data']['audit'][-1]['action'],'reviewed_inputs_revised')
  self.assertEqual(self.client.post(f'/api/projects/{p}/reviewed-inputs',json={'inputs':m,'change_reason':' '}).status_code,422)
 def test_failed_job_recoverable(self):
  from unittest.mock import patch
  p=self.create();self.upload(p,FIXTURES/'synthetic-house.dxf','foundation')
  with patch('foundation_mvp.pipeline.files_for_run',side_effect=RuntimeError('fixture failure')):
   r=self.client.post(f'/api/projects/{p}/process').json()['data'];done=self.wait(p,r['id']);self.assertEqual(done['status'],'failed')
  self.assertEqual(self.client.get(f'/api/projects/{p}').json()['data']['status'],'failed')
if __name__=='__main__':unittest.main()
