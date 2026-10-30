import {render,screen,within} from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import {beforeEach,expect,it,vi} from 'vitest';
import Workspace from '../components/workspace';
import {api,download} from '../lib/api';
import type {ProjectData} from '../lib/schemas';
vi.mock('../lib/api',()=>({api:vi.fn(),download:vi.fn(),message:(e:Error)=>e.message}));
const id='a'.repeat(32);
const base:ProjectData={id,name:'Test project',created_at:'2026-01-01T00:00:00Z',status:'not_started',files:[],job:null,outputs:[],summary:{}};
function mockProject(p:ProjectData){vi.mocked(api).mockImplementation(async(path)=>{
 if(path===`/projects/${id}`)return p;
 if(path.endsWith('/files'))throw new Error('Upload rejected by backend');
 if(path.endsWith('/issues'))return [{id:'ISS-1',severity:'error',category:'coordinates',description:'Alignment failed',impact:'Matching blocked',next_action:'Confirm control points',plot_id:'1',corner:1,source_file:'plan.dxf',source_entity:'A1'}];
 if(path.endsWith('/calculations'))return [{id:'1-1',plot_id:'1',corner:1,ground_level:98.98,bearing_level:97.95,reason:'Pipe',status:'calculated',review_status:'synthetic_test',explanation:'Pipe is the lowest candidate',candidates:[{reason:'Pipe',level:'97.950',steps:['98.200 - 0.300 = 97.900']}],sources:[{file:'plan.dxf',entity:'A1'}]}];
 if(path.includes('/extraction'))return {total:0,records:[],offset:0,limit:100};
 return [];
 });}
const completed={...base,status:'requires_review',job:{id:'b'.repeat(32),status:'completed_with_issues',current_stage:'Output verification',stages:[]}};
beforeEach(()=>{vi.mocked(api).mockReset();vi.mocked(download).mockReset();window.history.replaceState(null,'','#');});
it('shows no-files and no-run states',async()=>{mockProject(base);render(<Workspace id={id}/>);expect(await screen.findByText(/No source files uploaded/)).toBeInTheDocument();await userEvent.click(screen.getByRole('button',{name:/Processing/}));expect(screen.getByText(/Upload files and start the backend workflow/)).toBeInTheDocument();});
it('shows rejected upload errors',async()=>{mockProject(base);render(<Workspace id={id}/>);await screen.findByLabelText('Choose source files');const input=screen.getByLabelText('Choose source files');await userEvent.upload(input,new File(['bad'],'bad.dxf'));expect(await screen.findByRole('alert')).toBeInTheDocument();});
it('shows calculation evidence in an accessible dialog',async()=>{mockProject(completed);render(<Workspace id={id}/>);await screen.findByText('Test project');await userEvent.click(screen.getByRole('button',{name:/Calculations/}));await userEvent.click(await screen.findByRole('button',{name:'View calculation'}));expect(screen.getByRole('dialog')).toHaveTextContent('97.950');expect(screen.getByRole('dialog')).toHaveTextContent('plan.dxf');await userEvent.keyboard('{Escape}');expect(screen.queryByRole('dialog')).not.toBeInTheDocument();});
it('filters backend review issues',async()=>{mockProject(completed);render(<Workspace id={id}/>);await screen.findByText('Test project');await userEvent.click(screen.getByRole('button',{name:/Review issues/}));await screen.findByText('Alignment failed');await userEvent.selectOptions(screen.getByLabelText('Severity'),'warning');expect(screen.getByText('No issues match these filters.')).toBeInTheDocument();});
it('downloads only an available backend output',async()=>{mockProject({...completed,outputs:[{id:'out',name:'review.xlsx',kind:'review_workbook',verified:true,schedule_complete:false}]});render(<Workspace id={id}/>);await screen.findByText('Test project');await userEvent.click(screen.getByRole('button',{name:/Outputs/}));await userEvent.click(await screen.findByRole('button',{name:'Download'}));expect(download).toHaveBeenCalledWith(id,'out','review.xlsx');});
