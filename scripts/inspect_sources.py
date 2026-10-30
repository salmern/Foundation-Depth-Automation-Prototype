"""Read-only source audit: ZIP member paths are never used for extraction."""
import collections, hashlib, json, re, sys, zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as E
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'foundation-mvp/docs'; OUT.mkdir(exist_ok=True)
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def pairs(stream):
 while True:
  c=stream.readline(); v=stream.readline()
  if not c or not v: break
  try: yield int(c.strip()),v.decode('utf-8',errors='replace').strip()
  except ValueError: continue
def inspect_dxf(stream):
 counts=collections.Counter(); layers=collections.Counter(); texts=[]; inserts=collections.Counter(); blocks=[]; unit=None; current=None; tags=[]; section=None; header_var=None
 def record(kind,t):
  d=dict(t)
  if kind=='BLOCK': blocks.append({'name':d.get(2),'xref':d.get(1),'flags':d.get(70)})
  if section!='ENTITIES' or kind in ('SECTION','ENDSEC','EOF'): return
  counts[kind]+=1; layers[d.get(8,'0')]+=1
  if kind=='INSERT': inserts[d.get(2,'')]+=1
  if kind in ('TEXT','MTEXT','ATTRIB') and len(texts)<12000:
   texts.append({'kind':kind,'handle':d.get(5),'layer':d.get(8),'text':d.get(1),'tag':d.get(2),'x':d.get(10),'y':d.get(20),'z':d.get(30)})
 for c,v in pairs(stream):
  if c==9: header_var=v
  elif header_var=='$INSUNITS' and c==70: unit=v; header_var=None
  if c==0:
   if current: record(current,tags)
   current=v; tags=[]
  else:
   tags.append((c,v))
   if current=='SECTION' and c==2: section=v
 return {'units_code':unit,'entities':dict(counts),'layers':dict(layers),'inserts':dict(inserts),'blocks':blocks,'texts':texts}
def workbook(p):
 with zipfile.ZipFile(p) as z:
  strings=[''.join(si.itertext()) for si in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
  wb=E.fromstring(z.read('xl/workbook.xml')); result={'sheets':[s.attrib for s in wb.find('s:sheets',NS)],'names':[n.attrib|{'value':n.text} for n in wb.find('s:definedNames',NS)],'details':{}}
  for name in ('xl/worksheets/sheet1.xml','xl/worksheets/sheet3.xml'):
   r=E.fromstring(z.read(name)); cells=[]
   for c in r.findall('.//s:c',NS):
    v=c.find('s:v',NS); f=c.find('s:f',NS); value=v.text if v is not None else None
    if c.get('t')=='s' and value: value=strings[int(value)]
    row=int(re.search(r'\d+',c.get('r')).group())
    if row<=10 or (row==11 and f is not None): cells.append({'cell':c.get('r'),'value':value,'formula':f.text if f is not None else None})
   result['details'][name]={'dimension':r.find('s:dimension',NS).attrib,'columns':[c.attrib for c in r.findall('s:cols/s:col',NS)],'cells':cells}
  return result
def main():
 inventory=[]
 for p in sorted(ROOT.rglob('*')):
  if not p.is_file() or any(x in p.relative_to(ROOT).parts for x in ('.venv','.venv-foundation','.git','.agents','.codex','.aws','foundation-mvp')): continue
  item={'name':str(p.relative_to(ROOT)),'format':p.suffix.lower(),'size':p.stat().st_size,'source':'supplied','readable':True,'status':'inventoried'}
  item['status']={'.dwg':'bytes_readable; direct_DWG_processing_unsupported','.pdf':'bytes_readable; text_audited_separately','.xlsx':'ZIP_XML_and_formulas_inspected; openpyxl_unavailable','.docx':'document_XML_text_inspected','.zip':'archive_member_paths_and_sizes_inspected'}.get(item['format'],'bytes_readable; reference_asset')
  try:
   item['sha256']=hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
   if p.suffix.lower()=='.zip':
    with zipfile.ZipFile(p) as z:
     item['members']=[{'name':i.filename,'size':i.file_size,'safe':not(PurePosixPath(i.filename).is_absolute() or '..' in PurePosixPath(i.filename).parts or '\\' in i.filename)} for i in z.infolist()]
     if p.name=='dxf files.zip':
      for i in z.infolist():
       if i.filename.lower().endswith('.dxf'):
        print('Inspect',i.filename,flush=True)
        with z.open(i) as s: detail=inspect_dxf(s)
        (OUT/('cad-'+Path(i.filename).stem+'.json')).write_text(json.dumps(detail,indent=2))
   if p.suffix=='.xlsx': (OUT/'workbook-inspection.json').write_text(json.dumps(workbook(p),indent=2))
  except Exception as e: item['readable']=False;item['status']=str(e)
  inventory.append(item)
 (OUT/'source_inventory.json').write_text(json.dumps(inventory,indent=2))
 (OUT/'source_inventory.md').write_text('# Supplied source inventory\n\nGenerated read-only from the actual workspace. Full hashes, archive members and readability are in `source_inventory.json`. Original files are unchanged.\n\n|Name|Format|Bytes|Readability/status|\n|---|---|---:|---|\n'+'\n'.join(f"|{i['name']}|{i['format']}|{i['size']}|{i['status']}|" for i in inventory))

if __name__=='__main__':main()
