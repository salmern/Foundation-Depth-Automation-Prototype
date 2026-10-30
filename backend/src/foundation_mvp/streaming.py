"""Bounded ASCII DXF inspection for large files; no entity execution or xref loading.

All values retain original drawing coordinates. This complements ezdxf for files
whose embedded OLE payload is disproportionate to their modelspace geometry.
"""
from collections import Counter
import math
from pathlib import Path

LIMIT = 100000
SUPPORTED = {'LINE','LWPOLYLINE','POLYLINE','VERTEX','ARC','CIRCLE','INSERT','TEXT','MTEXT','ATTRIB','ATTDEF','HATCH','SPLINE','DIMENSION','POINT','SEQEND'}

def entities(stream):
    """Yield entities while discarding opaque binary/OLE group-code payloads."""
    kind = None
    tags = []
    count = 0
    while True:
        code = stream.readline()
        if not code:
            break
        value = stream.readline()
        if not value:
            raise ValueError('Truncated DXF group-code pair')
        try:
            code = int(code.strip())
        except ValueError:
            raise ValueError('Invalid ASCII DXF group code') from None
        if code == 0:
            if kind is not None:
                yield kind, tags
            kind = value.decode('utf-8', errors='replace').strip()
            tags = []
            count = 0
        elif not (310 <= code <= 319):
            # OLE hex is intentionally never retained. Other very large entities
            # are bounded too; an explicit exception prevents silent truncation.
            count += 1
            if count > 500000:
                raise ValueError('Single DXF entity exceeds tag safety limit')
            tags.append((code, value.decode('utf-8', errors='replace').strip()))
    if kind is not None:
        yield kind, tags

def values(tags, code):
    return [value for key, value in tags if key == code]

def numeric(d, code, default=0.0):
    value = float(d.get(code, default))
    if not math.isfinite(value):
        raise ValueError('Nonfinite geometry')
    return value

def point(d, code=10):
    return [numeric(d,code),numeric(d,code+10),numeric(d,code+20)]

def record(kind, tags, source):
    d = dict(tags)
    r = {'source_file':source, 'source_entity':d.get(5,''), 'layer':d.get(8,'0'),
         'entity_type':kind,'status':'extracted_unclassified','invisible':d.get(60,'0')=='1'}
    try:
        if kind in ('TEXT','MTEXT','ATTRIB','ATTDEF'):
            r.update(text=''.join(v for c,v in tags if c in (1,3)) if kind=='MTEXT' else d.get(1,''),point=point(d))
            if kind in ('ATTRIB','ATTDEF'):
                r['tag']=d.get(2,'')
        elif kind=='INSERT':
            r.update(block=d.get(2,''),point=point(d),rotation=numeric(d,50),
                     scale=[numeric(d,c,1) for c in (41,42,43)],attributes=[],status='block_geometry_not_interpreted')
        elif kind=='LINE':
            r['points']=[point(d),point(d,11)]
        elif kind=='POINT':
            r['point']=point(d)
        elif kind in ('ARC','CIRCLE'):
            r.update(point=point(d),radius=numeric(d,40))
        elif kind=='LWPOLYLINE':
            xs=values(tags,10);ys=values(tags,20)
            if len(xs)!=len(ys):raise ValueError('Mismatched polyline coordinates')
            pts=[[float(x),float(y)] for x,y in zip(xs,ys)]
            if not all(math.isfinite(v) for p in pts for v in p):raise ValueError('Nonfinite polyline')
            r.update(points=pts,closed=bool(int(d.get(70,0))&1),bulges=values(tags,42))
        else:
            return None
    except (ValueError,OverflowError):
        return {k:v for k,v in r.items() if k in ('source_file','source_entity','layer','entity_type')} | {'status':'invalid_geometry','warning':'Invalid or nonfinite geometry rejected'}
    return r

def inspect_stream(stream, source):
    section=None;current_block=None;blocks=[];records=[];last_insert=None
    counts=Counter();layers=Counter();unsupported=Counter();units=0;header_var=None
    eof=False;invalid=0;truncated=False
    for kind,tags in entities(stream):
        d=dict(tags)
        if kind=='SECTION':
            section=d.get(2)
            if section=='HEADER':
                for code,value in tags:
                    if code==9:header_var=value
                    elif header_var=='$INSUNITS' and code==70:units=int(value);header_var=None
            continue
        if kind=='ENDSEC':section=None;continue
        if kind=='EOF':eof=True;continue
        if section=='BLOCKS':
            if kind=='BLOCK':
                current_block={'name':d.get(2,''),'base_point':point(d),'xref':d.get(1,''),'flags':int(d.get(70,0)),'entities':Counter(),'visible_number_labels':[],'circle_centres':[]}
                blocks.append(current_block)
            elif kind=='ENDBLK':
                current_block=None
            elif current_block is not None:
                current_block['entities'][kind]+=1
                if kind=='TEXT' and d.get(60,'0')!='1' and d.get(1,'').strip() in ('1','2','3','4'):
                    current_block['visible_number_labels'].append({'corner':int(d[1]),'source_entity':d.get(5,''),'point':point(d)})
                if kind=='CIRCLE' and d.get(60,'0')!='1':
                    current_block['circle_centres'].append(point(d))
            continue
        if section!='ENTITIES':continue
        counts[kind]+=1;layers[d.get(8,'0')]+=1
        if kind not in SUPPORTED:unsupported[kind]+=1
        if kind=='ATTRIB' and last_insert is not None:
            last_insert['attributes'].append({'tag':d.get(2,''),'value':d.get(1,''),'source_entity':d.get(5,''),'point':point(d)})
            continue
        if kind!='SEQEND':last_insert=None
        if len(records)>=LIMIT:
            truncated=True;continue
        r=record(kind,tags,source)
        if r is not None:
            records.append(r)
            invalid+=r['status']=='invalid_geometry'
            if kind=='INSERT':last_insert=r
    if not eof:raise ValueError('DXF EOF marker missing')
    for block in blocks:block['entities']=dict(block['entities'])
    result={'source_file':source,'units_code':units,'entity_counts':dict(counts),'layers':dict(layers),
            'blocks':blocks,'unsupported_entities':dict(unsupported),'invalid_geometry_count':invalid,
            'records':records,'truncated':truncated,'reader':'bounded_ascii_stream',
            'scope':'Raw ASCII DXF modelspace. OLE binary payload not retained. Coordinates unchanged; semantic associations require review.'}
    annotate_markers(result)
    return result

def annotate_markers(drawing):
    """Resolve visible numeric label, never infer a physical house corner."""
    blocks={b['name']:b for b in drawing['blocks']}
    for r in drawing['records']:
        if r['entity_type']!='INSERT' or r['layer'].casefold()!='4 corner_100':continue
        block=blocks.get(r.get('block'),{})
        labels=block.get('visible_number_labels',[])
        if len(labels)==1 and block.get('circle_centres')==[[0.0,0.0,0.0]] and block.get('base_point')==[0.0,0.0,0.0]:
            r.update(candidate_type='numbered_corner_marker',corner=labels[0]['corner'],
                     number_source_entity=labels[0]['source_entity'],status='numbered_marker_requires_geometric_review',
                     evidence='Exactly one visible number and one circle centred on block origin; physical house-corner association not established')
        else:
            r.update(candidate_type='ambiguous_corner_marker',status='ambiguous',evidence='Visible number/marker geometry is not uniquely resolved')

def inspect(path,source):
    with Path(path).open('rb') as stream:
        if stream.read(22).startswith(b'AutoCAD Binary DXF'):
            raise ValueError('Large binary DXF requires a smaller ASCII DXF export')
        stream.seek(0)
        return inspect_stream(stream,source)
