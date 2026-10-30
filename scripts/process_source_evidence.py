"""Exercise the real bounded reader against the nine supplied DXF archive members."""
import json,sys,time,zipfile
from collections import Counter
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'backend/src'))
from foundation_mvp.streaming import inspect_stream

def main():
    results=[]
    with zipfile.ZipFile(BASE.parent/'dxf files.zip') as archive:
        for member in archive.infolist():
            if not member.filename.lower().endswith('.dxf'):continue
            started=time.monotonic();print('Reading '+member.filename,flush=True)
            with archive.open(member) as stream:drawing=inspect_stream(stream,member.filename)
            markers=[r for r in drawing['records'] if r.get('candidate_type') in ('numbered_corner_marker','ambiguous_corner_marker')]
            labels=[r for r in drawing['records'] if r['layer'].casefold()=='plot number' and r.get('text')]
            results.append({k:drawing[k] for k in ('source_file','units_code','entity_counts','layers','unsupported_entities','invalid_geometry_count','truncated','reader')}|{'records_extracted':len(drawing['records']),'numbered_markers':markers,'plot_labels':labels,'visible_corner_number_counts':dict(Counter(r.get('corner') for r in markers)),'elapsed_seconds':round(time.monotonic()-started,2)})
    (BASE/'outputs/streamed-source-evidence.json').write_text(json.dumps({'status':'raw_evidence_only','schedule_complete':False,'drawings':results},indent=2))
    print('All nine supplied DXFs parsed. Results remain raw evidence requiring engineering association.',flush=True)
if __name__=='__main__':main()
