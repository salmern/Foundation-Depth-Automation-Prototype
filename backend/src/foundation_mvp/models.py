from typing import Annotated,Literal
from pydantic import BaseModel,ConfigDict,Field,FiniteFloat,field_validator,BeforeValidator,StrictBool

def _numeric_input(value):
 if isinstance(value,bool):raise ValueError('Boolean values are not engineering numbers')
 return value
EngineeringNumber=Annotated[FiniteFloat,BeforeValidator(_numeric_input)]
Reason=Literal['Min Depth','Old Trees','New Tree','Geology','WPL','Pipe','Manhole']
class Strict(BaseModel): model_config=ConfigDict(extra='forbid')
class ProjectCreate(Strict):
 name: str=Field(min_length=1,max_length=120)
 @field_validator('name')
 @classmethod
 def printable(cls,v):
  if not v.strip() or any(ord(c)<32 for c in v):raise ValueError('Use a printable project name')
  return v.strip()
class SourceRef(Strict):
 file: str=Field(min_length=1,max_length=220)
 entity: str=Field(min_length=1,max_length=120)
class Constraint(Strict):
 reason:Reason
 applicability:Literal['applicable','inapplicable','unknown']
 explanation:str=Field(min_length=1,max_length=2000)
 sources:list[SourceRef]=Field(min_length=1)
 level_m:EngineeringNumber|None=None
 invert_m:EngineeringNumber|None=None
 centre_distance_m:Annotated[EngineeringNumber,Field(ge=0,le=3)]|None=None
 diameter_m:Annotated[EngineeringNumber,Field(gt=0)]|None=None
 competent_strata:StrictBool|None=None
 minimum_depth_m:Annotated[EngineeringNumber,Field(gt=0)]|None=None
class Corner(Strict):
 corner:Literal[1,2,3,4]
 @field_validator('corner',mode='before')
 @classmethod
 def integer_corner(cls,v):
  if type(v) is not int:raise ValueError('Corner must be an integer from 1 to 4')
  return v
 point:tuple[EngineeringNumber,EngineeringNumber]
 ground_level_m:EngineeringNumber|None=None
 sources:list[SourceRef]=Field(min_length=1)
 constraints:list[Constraint]=Field(min_length=7,max_length=7)
 @field_validator('constraints')
 @classmethod
 def all_reasons(cls,v):
  if len({c.reason for c in v})!=7:raise ValueError('Exactly one applicability decision is required for each of the seven reason codes')
  return v
class Plot(Strict):
 plot_id:str=Field(pattern=r'^[A-Za-z0-9][A-Za-z0-9 ._-]{0,39}$')
 house_type:str|None=None
 ffl_m:EngineeringNumber|None=None
 corners:list[Corner]=Field(min_length=4,max_length=4)
 @field_validator('corners')
 @classmethod
 def unique_corners(cls,v):
  if len({c.corner for c in v})!=4:raise ValueError('Corners 1–4 must occur exactly once')
  return v
class Reference(Strict):
 id:str=Field(min_length=1)
 source:tuple[EngineeringNumber,EngineeringNumber]
 target:tuple[EngineeringNumber,EngineeringNumber]
 evidence:str=Field(min_length=1)
class Alignment(Strict):
 source_file:str
 target_file:str
 tolerance_m:Annotated[EngineeringNumber,Field(gt=0)]
 justification:str=Field(min_length=1)
 references:list[Reference]=Field(min_length=4,max_length=100)
class ReviewedInputs(Strict):
 schema_version:Literal[1]
 dataset_kind:Literal['synthetic_test','engineer_reviewed']
 reviewer:str=Field(min_length=1,max_length=120)
 review_reason:str=Field(min_length=1,max_length=2000)
 units:Literal['m']
 alignments:list[Alignment]=[]
 @field_validator('alignments')
 @classmethod
 def unique_comparisons(cls,v):
  seen=set()
  for a in v:
   pair=frozenset((a.source_file,a.target_file))
   if len(pair)!=2 or pair in seen:raise ValueError('Alignment comparisons must be distinct drawings with one unambiguous comparison per pair')
   seen.add(pair)
  return v
 plots:list[Plot]=Field(min_length=1,max_length=2000)
 @field_validator('plots')
 @classmethod
 def unique_plots(cls,v):
  if len({p.plot_id for p in v})!=len(v):raise ValueError('Duplicate plot identifier')
  return v
class Envelope(BaseModel):
 data:dict|list
class ErrorResponse(BaseModel):
 error:dict

# Response schemas intentionally exclude server filesystem paths.
from typing import Generic,TypeVar,Any
T=TypeVar('T')
class ApiResponse(BaseModel,Generic[T]):data:T
class FileView(BaseModel):
 id:str
 name:str
 extension:str
 size:int
 category:str
 sha256:str
 uploaded_at:str
 upload_status:str
 validation_status:str
 processing_status:str
class StageView(BaseModel):
 name:str
 status:str
 message:str|None=None
 updated_at:str|None=None
class JobView(BaseModel):
 id:str
 status:str
 started_at:str
 current_stage:str|None=None
 stages:list[StageView]
 finished_at:str|None=None
 error:str|None=None
class OutputView(BaseModel):
 id:str
 name:str
 kind:str
 verified:bool
 schedule_complete:bool
 warning:str|None=None
 preserved_formulas:int|None=None
class ProjectView(BaseModel):
 id:str
 name:str
 created_at:str
 status:str
 files:list[FileView]
 job:JobView|None
 outputs:list[OutputView]
 summary:dict[str,int|bool]
 audit:list[dict[str,Any]]
class IssueView(BaseModel):
 id:str
 severity:Literal['error','warning','info']
 category:str
 description:str
 impact:str
 next_action:str
 source_file:str|None=None
 source_entity:str|None=None
 plot_id:str|None=None
 corner:int|None=None
class ExtractionView(BaseModel):
 records:list[dict[str,Any]]
 total:int
 offset:int
 limit:int

class ReviewRevision(Strict):
 inputs:ReviewedInputs
 change_reason:str=Field(min_length=3,max_length=2000)
