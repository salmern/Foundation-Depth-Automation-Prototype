"""Regression tests for streaming evidence, populated draft mapping and revisions."""
import copy,io,json,sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from foundation_mvp.streaming import inspect_stream
from foundation_mvp.excel import schedule_plan
from foundation_mvp.engineering import minimum_depth,excavation,select
from foundation_mvp import storage
from foundation_mvp.review import current_inputs,save_revision
FIXTURES=Path(__file__).parent/'fixtures'
def dxf(tags):return io.BytesIO(''.join(f'{code}\n{value}\n' for code,value in tags).encode())
def wrap(tags):return [(0,'SECTION'),(2,'ENTITIES')]+tags+[(0,'ENDSEC'),(0,'EOF')]
class StreamingTests(unittest.TestCase):
 def test_actual_synthetic_points_and_line(self):
  with (FIXTURES/'synthetic-house.dxf').open('rb') as stream:d=inspect_stream(stream,'synthetic-house.dxf')
  self.assertEqual(d['entity_counts'],{'POINT':4,'LINE':1});self.assertEqual(len(d['records']),5);self.assertEqual(d['units_code'],6)
 def test_invisible_numbers_are_not_selected(self):
  tags=[(0,'SECTION'),(2,'BLOCKS'),(0,'BLOCK'),(2,'MARKER'),(10,0),(20,0),(30,0),(0,'TEXT'),(5,'1'),(1,'1'),(60,1),(0,'TEXT'),(5,'2'),(1,'2'),(0,'CIRCLE'),(10,0),(20,0),(30,0),(40,1),(0,'ENDBLK'),(0,'ENDSEC')]+wrap([(0,'INSERT'),(5,'3'),(8,'4 Corner_100'),(2,'MARKER'),(10,10),(20,20)])
  result=inspect_stream(dxf(tags),'markers.dxf')['records'][0]
  self.assertEqual(result['corner'],2);self.assertEqual(result['point'],[10,20,0]);self.assertEqual(result['status'],'numbered_marker_requires_geometric_review')
 def test_two_visible_numbers_remain_ambiguous(self):
  tags=[(0,'SECTION'),(2,'BLOCKS'),(0,'BLOCK'),(2,'M'),(0,'TEXT'),(1,'1'),(0,'TEXT'),(1,'2'),(0,'ENDBLK'),(0,'ENDSEC')]+wrap([(0,'INSERT'),(8,'4 Corner_100'),(2,'M')])
  self.assertEqual(inspect_stream(dxf(tags),'a')['records'][0]['status'],'ambiguous')
 def test_opaque_ole_payload_not_retained(self):
  result=inspect_stream(dxf(wrap([(0,'OLE2FRAME'),(310,'AB'*10000),(0,'POINT'),(5,'A1'),(10,2),(20,3)])),'a')
  self.assertEqual(result['unsupported_entities'],{'OLE2FRAME':1});self.assertEqual(len(result['records']),1)
 def test_missing_eof_rejected(self):
  with self.assertRaises(ValueError):inspect_stream(dxf([(0,'SECTION'),(2,'ENTITIES')]),'a')
 def test_nonfinite_geometry_rejected(self):
  result=inspect_stream(dxf(wrap([(0,'POINT'),(10,'nan'),(20,0)])),'a')
  self.assertEqual(result['invalid_geometry_count'],1);self.assertEqual(result['records'][0]['status'],'invalid_geometry')
 def test_multiline_text_segments_preserved(self):
  result=inspect_stream(dxf(wrap([(0,'MTEXT'),(3,'ABC'),(3,'DEF'),(1,'GHI')])),'a')
  self.assertEqual(result['records'][0]['text'],'ABCDEFGHI')
 def test_attributes_stay_attached_to_insert(self):
  result=inspect_stream(dxf(wrap([(0,'INSERT'),(5,'I'),(2,'SPOT'),(0,'ATTRIB'),(5,'A'),(2,'LEVEL'),(1,'98.20'),(0,'SEQEND')])),'a')
  self.assertEqual(result['records'][0]['attributes'][0]['value'],'98.20')
class DraftMappingTests(unittest.TestCase):
 def data(self):
  m=json.loads((FIXTURES/'synthetic-reviewed-inputs.json').read_text());plot=m['plots'][0];records=[]
  for c in plot['corners']:
   candidates=[minimum_depth(c['ground_level_m'])]
   if c['corner']==1:candidates.append(excavation(98.2,.6,.1,competent=True))
   records.append({'plot_id':plot['plot_id'],'corner':c['corner'],**select(candidates)})
  return {'plots':[plot],'calculations':records}
 def test_known_output_mapping_and_independent_expected_values(self):
  p=schedule_plan(self.data());self.assertEqual(p['cells']['A10'],'TEST-R2G');self.assertEqual(p['cells']['I10'],'Pipe');self.assertEqual(p['cells']['U10'],97.95);self.assertEqual(p['cells']['V10'],97.94);self.assertEqual(p['cells']['W10'],97.87);self.assertEqual(p['cells']['X10'],97.9);self.assertEqual(p['calculated_corners'],4);self.assertFalse(p['schedule_complete'])
 def test_blocked_corner_has_no_fake_value_or_reason(self):
  d=self.data();d['calculations'][0]['status']='blocked';p=schedule_plan(d)
  self.assertIsNone(p['cells']['U10']);self.assertIsNone(p['cells']['I10']);self.assertIsNone(p['cells']['Y10']);self.assertEqual(p['review_corners'],1)
 def test_duplicate_corner_rejected(self):
  d=self.data();d['calculations'].append(d['calculations'][0])
  with self.assertRaises(ValueError):schedule_plan(d)
 def test_unsupported_reason_rejected(self):
  d=self.data();d['calculations'][0]['reason']='Vibro'
  with self.assertRaises(ValueError):schedule_plan(d)
 def test_empty_results_rejected(self):
  with self.assertRaises(ValueError):schedule_plan({'plots':[],'calculations':[]})
  from foundation_mvp.excel import export_review
  with self.assertRaises(ValueError):export_review('source.xlsx','source.xlsx',{})
class RevisionTests(unittest.TestCase):
 def setUp(self):self.temp=tempfile.TemporaryDirectory();self.old=storage.ROOT;storage.ROOT=Path(self.temp.name);self.p=storage.create('Review project');self.inputs=json.loads((FIXTURES/'synthetic-reviewed-inputs.json').read_text())
 def tearDown(self):storage.ROOT=self.old;self.temp.cleanup()
 def test_first_revision_loads(self):
  r=save_revision(self.p,self.inputs,'Initial review');self.assertEqual(current_inputs(self.p)['revision'],r['revision'])
 def test_previous_values_preserved_and_stale_results_cleared(self):
  first=save_revision(self.p,self.inputs,'Initial review');old_file=self.p['files'][0]['stored_name'];changed=copy.deepcopy(self.inputs);changed['plots'][0]['ffl_m']=99.3;self.p['results']={'stale':True};save_revision(self.p,changed,'Corrected FFL from source')
  self.assertIsNone(self.p['results']);self.assertEqual(len(self.p['files']),1);self.assertEqual(json.loads((storage.directory(self.p['id'])/'sources'/old_file).read_text())['plots'][0]['ffl_m'],99.2);self.assertEqual(self.p['audit'][-1]['previous_revisions'][0]['id'],first['revision']);self.assertEqual(self.p['audit'][-1]['reason'],'Corrected FFL from source')
 def test_revision_reason_required(self):
  with self.assertRaises(ValueError):save_revision(self.p,self.inputs,' ')
 def test_reviewer_required(self):
  self.inputs['reviewer']=' '
  with self.assertRaises(ValueError):save_revision(self.p,self.inputs,'Review change')
if __name__=='__main__':unittest.main()
