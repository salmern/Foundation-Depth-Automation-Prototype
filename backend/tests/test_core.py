import io,json,math,sys,tempfile,unittest,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from foundation_mvp.engineering import EngineeringError,brief_example,excavation,minimum_depth,select
from foundation_mvp.geometry import alignment,match_point,transform
from foundation_mvp.safety import filename,archive_members,InputError
from foundation_mvp import storage
class EngineeringTests(unittest.TestCase):
 def test_independent_brief_example(self):
  r=brief_example();self.assertEqual(r['bearing_level'],97.950);self.assertEqual(r['reason'],'Pipe')
  self.assertEqual(r['candidates'][0]['level'],'98.080');self.assertEqual(r['candidates'][1]['level'],'97.950')
  self.assertIn('97.900',r['candidates'][1]['steps'][0]);self.assertIn('0.050',r['candidates'][1]['steps'][1])
 def test_minimum(self):self.assertEqual(minimum_depth(100)['level'],'99.100')
 def test_missing_not_zero(self):
  with self.assertRaises(EngineeringError):minimum_depth(None)
 def test_invalid_numbers(self):
  for x in ['nan','inf','bad',True]:
   with self.subTest(x=x),self.assertRaises(EngineeringError):minimum_depth(x)
 def test_fallback(self):
  r=excavation(98.2,.6,competent=True);self.assertTrue(r['fallback_used']);self.assertEqual(r['inputs']['diameter_m'],'0.100')
 def test_no_manhole_fallback(self):
  with self.assertRaises(EngineeringError):excavation(98.2,.6,kind='Manhole',competent=True)
 def test_invalid_diameters(self):
  for dia in [0,-1,'bad']:
   with self.subTest(dia=dia),self.assertRaises(EngineeringError):excavation(98.2,.6,dia,competent=True)
 def test_competency_required(self):
  with self.assertRaises(EngineeringError):excavation(98.2,.6,.1)
 def test_distance(self):
  for d in [-.1,3.01,None]:
   with self.subTest(d=d),self.assertRaises(EngineeringError):excavation(98.2,d,.1,competent=True)
 def test_negative_clear_clamped_per_workbook(self):
  r=excavation(98.2,0,.1,competent=True);self.assertEqual(float(r['level']),97.9);self.assertTrue(r['warnings'])
 def test_tie_priority_from_actual_template(self):
  r=select([{'reason':'Min Depth','level':'98'},{'reason':'Pipe','level':'98'}]);self.assertEqual(r['reason'],'Pipe');self.assertEqual(len(r['controlling_constraints']),2)
 def test_no_candidates(self):
  with self.assertRaises(EngineeringError):select([])
 def test_unknown_reason(self):
  with self.assertRaises(EngineeringError):select([{'reason':'Vibro','level':98}])
 def test_precision(self):self.assertEqual(select([{'reason':'Pipe','level':'97.9505'}])['bearing_level'],97.951)
 def test_all_valid_reasons(self):
  for reason in ['Old Trees','New Tree','Geology','WPL','Manhole']:
   self.assertEqual(select([{'reason':reason,'level':'98'}])['reason'],reason)
class GeometryTests(unittest.TestCase):
 def refs(self,reflect=False):
  points=[(0,0),(10,0),(0,10),(5,6)]
  return [{'id':str(i),'source':p,'target':(-2*p[1]+100,2*p[0]+200) if not reflect else (-p[0],p[1]),'evidence':'synthetic independent control'} for i,p in enumerate(points)]
 def test_similarity_with_independent_holdout(self):
  r=alignment(self.refs(),.001,'Synthetic fixture metre controls');self.assertEqual(r['status'],'validated');self.assertAlmostEqual(r['transformation']['scale'],2);self.assertAlmostEqual(r['transformation']['rotation_degrees'],90);self.assertLess(r['max_residual'],1e-10)
 def test_reflection_rejected(self):self.assertEqual(alignment(self.refs(True),.01,'test')['status'],'blocked')
 def test_insufficient(self):self.assertEqual(alignment(self.refs()[:3],.01,'test')['status'],'blocked')
 def test_no_tolerance(self):self.assertEqual(alignment(self.refs(),0,'test')['status'],'blocked')
 def test_missing_justification(self):self.assertEqual(alignment(self.refs(),.1,'')['status'],'blocked')
 def test_holdout_outlier(self):
  refs=self.refs();refs[-1]['target']=(1,1);self.assertEqual(alignment(refs,.1,'test')['status'],'blocked')
 def test_collinear(self):
  r=[{'id':str(i),'source':(i,0),'target':(i,1)} for i in range(4)];self.assertEqual(alignment(r,.1,'test')['status'],'blocked')
 def test_duplicate_controls(self):
  r=self.refs();r[1]['id']=r[0]['id'];self.assertEqual(alignment(r,.1,'test')['status'],'blocked')
 def test_repeated_control_coordinates(self):
  r=self.refs();r[-1]['source']=r[0]['source'];self.assertEqual(alignment(r,.1,'test')['status'],'blocked')
 def test_unique_match(self):self.assertEqual(match_point((0,0),[{'id':'a','point':(.05,0)}],.1,'test')['status'],'matched')
 def test_multiple_matches_not_nearest(self):self.assertEqual(match_point((0,0),[{'id':'a','point':(.01,0)},{'id':'b','point':(.02,0)}],.1,'test')['status'],'ambiguous')
 def test_unmatched(self):self.assertEqual(match_point((0,0),[{'id':'a','point':(1,0)}],.1,'test')['status'],'unmatched')
 def test_threshold_required(self):
  with self.assertRaises(ValueError):match_point((0,0),[],1,'')
class FileSafetyTests(unittest.TestCase):
 def test_bad_names(self):
  for n in ['../file.dxf','/file.dxf','a\\b.xlsx','bad\x00.dxf','a.exe','']:
   with self.subTest(n=n),self.assertRaises(InputError):filename(n)
 def test_good_name(self):self.assertEqual(filename('Drainage A.DXF'),'.dxf')
 def test_traversal_archives(self):
  for n in ['../a.dxf','/a.dxf','x\\a.dxf','C:/a.dxf']:
   with tempfile.TemporaryDirectory() as d:
    p=Path(d)/'test.zip'
    with zipfile.ZipFile(p,'w') as z:z.writestr(n,'contents')
    with self.assertRaises(InputError):archive_members(p)
 def test_symlink_archive(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'symlink.zip';i=zipfile.ZipInfo('model.dxf');i.create_system=3;i.external_attr=(0o120777 << 16)
   with zipfile.ZipFile(p,'w') as z:z.writestr(i,'/etc/passwd')
   with self.assertRaises(InputError):archive_members(p)
 def test_duplicate_archive_names(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'dup.zip'
   with zipfile.ZipFile(p,'w') as z:z.writestr('a.dxf','a');z.writestr('A.dxf','b')
   with self.assertRaises(InputError):archive_members(p)
 def test_safe_zip(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.zip'
   with zipfile.ZipFile(p,'w') as z:z.writestr('models/a.dxf','contents')
   self.assertEqual(len(archive_members(p)),1)
 def test_corrupt_zip(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'test.zip';p.write_text('not zip')
   with self.assertRaises(InputError):archive_members(p)
class StorageTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.old=storage.ROOT;storage.ROOT=Path(self.tmp.name)
 def tearDown(self):storage.ROOT=self.old;self.tmp.cleanup()
 def test_project_survives_reload(self):
  p=storage.create('Site A');self.assertEqual(storage.load(p['id'])['name'],'Site A');self.assertEqual(len(storage.list_projects()),1)
 def test_invalid_id(self):
  with self.assertRaises(ValueError):storage.load('../../etc')
 def test_recovery(self):
  p=storage.create('Site A');p['job']={'status':'running'};storage.save(p);storage.recover();self.assertEqual(storage.load(p['id'])['job']['status'],'interrupted')
 def test_invalid_name(self):
  with self.assertRaises(ValueError):storage.create('  ')

class PipelineLifecycleTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.old=storage.ROOT;storage.ROOT=Path(self.tmp.name)
 def tearDown(self):storage.ROOT=self.old;self.tmp.cleanup()
 def seeded(self):
  p=storage.create('Pipeline lifecycle test');root=storage.directory(p['id']);(root/'sources').mkdir();source=root/'sources'/'source.pdf';source.write_bytes(b'%PDF-1.0 test reference')
  p['files']=[{'id':storage.uid(),'name':'reference.pdf','stored_name':'source.pdf','extension':'.pdf','category':'reference','processing_status':'queued'}]
  from foundation_mvp.pipeline import STAGES
  p['job']={'id':storage.uid(),'status':'queued','stages':[{'name':s,'status':'pending'} for s in STAGES]};storage.save(p);return p,source
 def test_reference_only_run_creates_real_report_and_retains_blocks(self):
  from foundation_mvp.pipeline import run
  p,source=self.seeded();run(p['id']);saved=storage.load(p['id'])
  self.assertEqual(saved['job']['status'],'completed_with_issues');self.assertEqual(saved['results']['summary']['corners_calculated'],0)
  self.assertEqual(saved['job']['stages'][6]['status'],'blocked');self.assertEqual(saved['job']['stages'][8]['status'],'blocked')
  self.assertEqual(saved['files'][0]['processing_status'],'reference_only');self.assertTrue(source.exists())
  report=storage.directory(p['id'])/saved['outputs'][0]['path'];self.assertTrue(report.exists());self.assertFalse(json.loads(report.read_text())['summary']['schedule_complete'])
 def test_workflow_exception_marks_failed_and_preserves_source(self):
  from foundation_mvp.pipeline import run
  from unittest.mock import patch
  p,source=self.seeded()
  with patch('foundation_mvp.pipeline.files_for_run',side_effect=RuntimeError('injected unit-test failure')):
   with self.assertLogs('foundation_mvp.pipeline',level='ERROR'):run(p['id'])
  saved=storage.load(p['id']);self.assertEqual(saved['job']['status'],'failed');self.assertEqual(saved['job']['stages'][0]['status'],'failed');self.assertTrue(source.exists())

class StreamingInspectionTests(unittest.TestCase):
 def test_entity_counts_exclude_section_boundaries(self):
  import importlib.util
  script=Path(__file__).resolve().parents[2]/'scripts/inspect_sources.py'
  spec=importlib.util.spec_from_file_location('source_audit',script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  with (Path(__file__).parent/'fixtures/synthetic-house.dxf').open('rb') as stream:result=module.inspect_dxf(stream)
  self.assertEqual(result['entities'],{'POINT':4,'LINE':1});self.assertEqual(result['units_code'],'6')

if __name__=='__main__':unittest.main()
