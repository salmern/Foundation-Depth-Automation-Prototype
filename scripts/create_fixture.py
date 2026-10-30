"""Synthetic test evidence, clearly separate from supplied client drawings."""
import json
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]/'backend/tests/fixtures';OUT.mkdir(exist_ok=True,parents=True)
# Valid minimal ASCII DXF with four explicit 3D point entities and stable handles.
tags=[(0,'SECTION'),(2,'HEADER'),(9,'$ACADVER'),(1,'AC1015'),(9,'$INSUNITS'),(70,6),(0,'ENDSEC'),(0,'SECTION'),(2,'ENTITIES')]
for i,(x,y,z) in enumerate([(0,0,98.980),(10,0,98.84),(10,8,98.77),(0,8,98.80)],start=1):
 tags.extend([(0,'POINT'),(5,f'A{i}'),(8,'SYNTHETIC_CORNERS'),(10,x),(20,y),(30,z)])
tags.extend([(0,'LINE'),(5,'B1'),(8,'SYNTHETIC_DRAIN'),(10,.6),(20,-2),(30,98.2),(11,.6),(21,10),(31,98.2),(0,'ENDSEC'),(0,'EOF')])
(OUT/'synthetic-house.dxf').write_text(''.join(f'{k}\n{v}\n' for k,v in tags))
plots=[];corners=[]
for i,(x,y,z) in enumerate([(0,0,98.980),(10,0,98.84),(10,8,98.77),(0,8,98.80)],start=1):
 source={'file':'synthetic-house.dxf','entity':f'A{i}'}
 constraints=[]
 for reason in ['Min Depth','Old Trees','New Tree','Geology','WPL','Pipe','Manhole']:
  c={'reason':reason,'applicability':'inapplicable','explanation':'Synthetic fixture explicitly excludes this constraint. This is not site evidence.','sources':[source]}
  if reason=='Min Depth':c.update(applicability='applicable',minimum_depth_m=.9,explanation='Synthetic medium-volume clay case with reviewed minimum depth.')
  if reason=='Pipe' and i==1:c.update(applicability='applicable',invert_m=98.2,centre_distance_m=.6,diameter_m=.1,competent_strata=True,sources=[{'file':'synthetic-house.dxf','entity':'B1'}],explanation='Synthetic replication of build brief example.')
  constraints.append(c)
 corners.append({'corner':i,'point':[x,y],'ground_level_m':z,'sources':[source],'constraints':constraints})
manifest={'schema_version':1,'dataset_kind':'synthetic_test','reviewer':'Synthetic fixture author','review_reason':'Independently specified test inputs. Not client drawing extraction.','units':'m','alignments':[],'plots':[{'plot_id':'TEST-R2G','house_type':'Synthetic rectangle','ffl_m':99.2,'corners':corners}]}
(OUT/'synthetic-reviewed-inputs.json').write_text(json.dumps(manifest,indent=2))
