import {afterEach,describe,expect,it,vi} from 'vitest';
import {z} from 'zod';
import {api} from '../lib/api';
afterEach(()=>vi.restoreAllMocks());
describe('API boundary',()=>{
 it('rejects a malformed successful response',async()=>{vi.stubGlobal('fetch',vi.fn().mockResolvedValue(new Response(JSON.stringify({data:{unexpected:true}}))));await expect(api('/test',z.object({id:z.string()}))).rejects.toThrow('unexpected format');});
 it('explains a network failure',async()=>{vi.stubGlobal('fetch',vi.fn().mockRejectedValue(new TypeError('network')));await expect(api('/test',z.object({}))).rejects.toThrow('Cannot reach the backend');});
 it('retains backend validation errors',async()=>{vi.stubGlobal('fetch',vi.fn().mockResolvedValue(new Response(JSON.stringify({error:{message:'File is empty'}}),{status:422})));await expect(api('/test',z.object({}))).rejects.toThrow('File is empty');});
 it('accepts schema-validated data',async()=>{vi.stubGlobal('fetch',vi.fn().mockResolvedValue(new Response(JSON.stringify({data:{id:'project'}}))));await expect(api('/test',z.object({id:z.string()}))).resolves.toEqual({id:'project'});});
});
