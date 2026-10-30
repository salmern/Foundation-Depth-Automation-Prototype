"""Evidence-based similarity fit; no default tolerance is an engineering approval."""
import math,statistics

def transform(point, t):
 x,y=point;return (t['a']*x-t['b']*y+t['tx'],t['b']*x+t['a']*y+t['ty'])
def alignment(references,tolerance,justification):
 if len(references)<4 or tolerance<=0 or not justification.strip():
  return {'status':'blocked','candidate_reference_points':len(references),'validated_reference_points':0,'reason':'At least four named independent references and an engineer-justified tolerance are required'}
 if len({tuple(r['source']) for r in references})!=len(references) or len({tuple(r['target']) for r in references})!=len(references):return {'status':'blocked','reason':'Repeated coordinates cannot serve as independent reference points'}
 # Fit using all but final independent held-out reference.
 train=references[:-1];src=[r['source'] for r in train];dst=[r['target'] for r in train]
 if len({r['id'] for r in references})!=len(references):return {'status':'blocked','reason':'Duplicate reference identifiers'}
 sx=statistics.mean(p[0] for p in src);sy=statistics.mean(p[1] for p in src);dx=statistics.mean(p[0] for p in dst);dy=statistics.mean(p[1] for p in dst)
 denominator=sum((x-sx)**2+(y-sy)**2 for x,y in src)
 # Reject collinear controls: cannot independently distinguish reflection.
 area=max(abs((p[0]-sx)*(q[1]-sy)-(p[1]-sy)*(q[0]-sx)) for p in src for q in src)
 if denominator<=0 or area<=1e-12:return {'status':'blocked','reason':'Degenerate or collinear reference geometry'}
 a=sum((p[0]-sx)*(q[0]-dx)+(p[1]-sy)*(q[1]-dy) for p,q in zip(src,dst))/denominator
 b=sum((p[0]-sx)*(q[1]-dy)-(p[1]-sy)*(q[0]-dx) for p,q in zip(src,dst))/denominator
 t={'a':a,'b':b,'tx':dx-a*sx+b*sy,'ty':dy-b*sx-a*sy,'scale':math.hypot(a,b),'rotation_degrees':math.degrees(math.atan2(b,a))}
 residuals=[math.dist(transform(r['source'],t),r['target']) for r in references]
 ordered=sorted(residuals);high=ordered[math.ceil(.95*len(ordered))-1]
 ok=max(residuals)<=tolerance and t['scale']>0
 return {'status':'validated' if ok else 'blocked','transformation':t,'candidate_reference_points':len(references),'validated_reference_points':sum(v<=tolerance for v in residuals),'median_residual':statistics.median(residuals),'p95_residual':high,'max_residual':max(residuals),'holdout_residual':residuals[-1],'tolerance_m':tolerance,'justification':justification,'references':references,'residuals':residuals,'method':'Orientation-preserving similarity; last reference held out from fitting'}
def match_point(point,features,threshold,justification):
 if threshold<=0 or not justification:raise ValueError('A justified positive matching threshold is required')
 candidates=sorted([{'id':f['id'],'distance':math.dist(point,f['point'])} for f in features],key=lambda c:(c['distance'],c['id']))
 within=[c for c in candidates if c['distance']<=threshold]
 return {'status':'matched' if len(within)==1 else 'ambiguous' if within else 'unmatched','candidate':within[0] if len(within)==1 else None,'alternatives':candidates,'rule':'Exactly one point within justified threshold; nearest alone is insufficient','threshold_m':threshold,'justification':justification}
def polygon_corners(points):
 from shapely.geometry import Polygon
 p=Polygon(points)
 if not p.is_valid or p.area<=0 or len(points)!=4:raise ValueError('Expected valid four-corner outline')
 return list(p.exterior.coords)[:-1]
