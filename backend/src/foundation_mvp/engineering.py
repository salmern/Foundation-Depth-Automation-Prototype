"""Deterministic, SI-unit calculation primitives. No CAD or UI dependencies."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
REASONS=('Min Depth','Old Trees','New Tree','Geology','WPL','Pipe','Manhole')
class EngineeringError(ValueError): pass
def number(value, name):
 if value is None or isinstance(value,bool): raise EngineeringError(f'{name} is missing or invalid')
 try: result=Decimal(str(value))
 except InvalidOperation: raise EngineeringError(f'{name} must be numeric') from None
 if not result.is_finite(): raise EngineeringError(f'{name} must be finite')
 return result
def rounded(x): return float(x.quantize(Decimal('.001'),rounding=ROUND_HALF_UP))
def minimum_depth(ground_level, depth='0.900'):
 ground=number(ground_level,'ground level'); d=number(depth,'minimum depth')
 if d<=0: raise EngineeringError('Minimum depth must be positive')
 return {'reason':'Min Depth','level':str(ground-d),'inputs':{'ground_level_m':str(ground),'minimum_depth_m':str(d)},'steps':[f'{ground} - {d} = {ground-d} m'],'source_rule':'Build brief; PDF Detail A (conditional clay minimum)'}
def excavation(invert, distance, diameter=None, kind='Pipe', competent=False):
 if kind not in ('Pipe','Manhole'): raise EngineeringError('Unknown excavation kind')
 if not competent: raise EngineeringError('Competent founding strata must be confirmed for 0.5 m allowance')
 il=number(invert,'invert'); dist=number(distance,'centre distance'); fallback=diameter is None and kind=='Pipe'
 dia=number('0.100' if fallback else diameter,'diameter')
 if dia<=0 or dist<0: raise EngineeringError('Diameter must be positive and distance nonnegative')
 if dist>3: raise EngineeringError('Outside source drawing 3 m service assessment scope')
 bottom=il-Decimal('.300');clear=dist-Decimal('.500')-dia/2;level=bottom+max(Decimal(0),clear)
 return {'reason':kind,'level':str(level),'inputs':{'invert_m':str(il),'distance_m':str(dist),'diameter_m':str(dia),'competent_strata':True},'steps':[f'Trench bottom: {il} - 0.300 = {bottom} m',f'Clear distance: {dist} - 0.500 - {dia}/2 = {clear} m',f'45 degree influence (clear distance clamped at zero per Input!AZ10): {bottom} + {max(Decimal(0),clear)} = {level} m'],'fallback_used':fallback,'warnings':(['100 mm pipe diameter fallback from build brief'] if fallback else [])+(['Corner lies within excavation allowance; engineer review required'] if clear<0 else []),'source_rule':'Foundation PDF Details Y/Z; build brief drainage example'}
def select(candidates):
 if not candidates: raise EngineeringError('No valid applicable constraints')
 for c in candidates:
  if c.get('reason') not in REASONS: raise EngineeringError('Unknown reason code')
  number(c.get('level'),'candidate level')
 low=min(number(c['level'],'level') for c in candidates)
 winners=[c['reason'] for c in candidates if number(c['level'],'level')==low]
 return {'bearing_level':rounded(low),'unrounded_level':str(low),'reason':next(r for r in ('WPL','Pipe','Manhole','Geology','Old Trees','New Tree','Min Depth') if r in winners),'controlling_constraints':winners,'status':'calculated','explanation':'Lowest bearing elevation requires the deepest foundation. '+('Tied candidates use the priority in template Input!CV10: WPL, Pipe, Manhole, Geology, Old Trees, New Tree, Min Depth.' if len(set(winners))>1 else winners[0]+' is the lowest candidate.'),'candidates':candidates,'units':'m'}
def brief_example():
 return select([minimum_depth('98.980'),excavation('98.200','.600','.100',competent=True)]) | {'provenance':'Source brief worked example R2G corner 1; not a result extracted from supplied site drawings'}
