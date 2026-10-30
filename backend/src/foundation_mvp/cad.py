"""ezdxf inspection with bounded extraction, source handles and explicit limitations."""
from collections import Counter
import re,json

def inspect(path,source):
 from pathlib import Path
 if Path(path).stat().st_size>80*1024*1024:
  from .streaming import inspect as stream_inspect
  return stream_inspect(path,source)
 import ezdxf
 doc=ezdxf.readfile(path);msp=doc.modelspace();counts=Counter();layers=Counter();records=[];blocks=[];unsupported=Counter();limit=100000;invalid_geometry=0
 for block in doc.blocks:
  blocks.append({'name':block.name,'base_point':list(block.base_point),'xref':block.block.dxf.get('xref_path',''),'flags':block.block.dxf.get('flags',0),'entities':dict(Counter(e.dxftype() for e in block)), 'visible_number_labels':[{'corner':int(e.dxf.text.strip()),'source_entity':e.dxf.handle,'point':list(e.dxf.insert)} for e in block if e.dxftype()=='TEXT' and not e.dxf.get('invisible',0) and e.dxf.text.strip() in ('1','2','3','4')], 'circle_centres':[list(e.dxf.center) for e in block if e.dxftype()=='CIRCLE' and not e.dxf.get('invisible',0)]})
 for e in msp:
  kind=e.dxftype();counts[kind]+=1;layers[e.dxf.layer]+=1
  if kind not in ('LINE','LWPOLYLINE','POLYLINE','ARC','CIRCLE','INSERT','TEXT','MTEXT','ATTRIB','ATTDEF','HATCH','SPLINE','DIMENSION','POINT'):unsupported[kind]+=1
  if len(records)>=limit:continue
  r={'source_file':source,'source_entity':e.dxf.handle,'layer':e.dxf.layer,'entity_type':kind,'status':'extracted_unclassified'}
  if kind in ('TEXT','MTEXT'):
   r.update(text=e.plain_text() if kind=='MTEXT' else e.dxf.text,point=list(e.dxf.insert))
   if re.fullmatch(r'[1-4]',r['text'].strip()):r['candidate_type']='corner_label'
   elif re.search(r'FFL\s*[=:]?',r['text'],re.I):r['candidate_type']='floor_level_text'
   elif re.search(r'\bIL\s*[:=]',r['text'],re.I):r['candidate_type']='invert_text'
   elif re.fullmatch(r'\d{1,3}\.\d{2,3}',r['text'].strip()):r['candidate_type']='elevation_text_unassociated'
  elif kind=='INSERT':
   r.update(block=e.dxf.name,point=list(e.dxf.insert),rotation=e.dxf.get('rotation',0),scale=[e.dxf.get(k,1) for k in ('xscale','yscale','zscale')],attributes=[{'tag':a.dxf.tag,'value':a.dxf.text,'source_entity':a.dxf.handle,'point':list(a.dxf.insert)} for a in e.attribs]);r['status']='block_geometry_not_interpreted'
  elif kind=='LINE':r.update(points=[list(e.dxf.start),list(e.dxf.end)])
  elif kind=='LWPOLYLINE':r.update(points=[list(p) for p in e.get_points('xyb')],closed=e.closed)
  elif kind in ('CIRCLE','ARC'):r.update(point=list(e.dxf.center),radius=e.dxf.radius)
  elif kind=='POINT':r.update(point=list(e.dxf.location))
  else:continue
  try:json.dumps(r,allow_nan=False)
  except ValueError:
   invalid_geometry+=1;r={k:v for k,v in r.items() if k in ('source_file','source_entity','layer','entity_type')}|{'status':'invalid_geometry','warning':'Nonfinite numeric geometry rejected'}
  records.append(r)
 result={'source_file':source,'units_code':doc.header.get('$INSUNITS',0),'entity_counts':dict(counts),'layers':dict(layers),'blocks':blocks,'unsupported_entities':dict(unsupported),'invalid_geometry_count':invalid_geometry,'records':records,'truncated':sum(counts.values())>limit,'scope':'Modelspace raw entities. Block definitions inventoried; inserts are not assumed to be house corners. No automatic text-to-feature semantic associations.'}

 from .streaming import annotate_markers
 annotate_markers(result)
 return result
