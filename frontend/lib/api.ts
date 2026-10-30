import {z} from 'zod';
export const BASE=(process.env.NEXT_PUBLIC_API_BASE_URL||'http://127.0.0.1:8000').replace(/\/$/,'');
export class ApiError extends Error{constructor(message:string,public status:number){super(message);}}
export async function api<T extends z.ZodTypeAny>(path:string,schema:T,options:RequestInit={}):Promise<z.infer<T>>{
 let response:Response;
 try{response=await fetch(`${BASE}/api${path}`,{...options,cache:'no-store'});}catch(error){if(error instanceof DOMException&&error.name==='AbortError')throw error;throw new ApiError('Cannot reach the backend. Check that the API is running, then retry.',0);}
 let body:unknown;
 try{body=await response.json();}catch{throw new ApiError('The backend returned an unreadable response.',response.status);}
 if(!response.ok){const parsed=z.object({error:z.object({message:z.string(),details:z.array(z.object({field:z.string(),message:z.string()})).optional()})}).safeParse(body);throw new ApiError(parsed.success?parsed.data.error.message+(parsed.data.error.details?.map(x=>` · ${x.field}: ${x.message}`).join('')||''):'The request failed.',response.status);}
 const envelope=z.object({data:schema}).safeParse(body);
 if(!envelope.success)throw new ApiError('The backend response has an unexpected format. Refresh or check compatible app versions.',response.status);
 return envelope.data.data;
}
export function message(error:unknown){return error instanceof Error?error.message:'The request failed. Please retry.';}
export async function download(projectId:string,outputId:string,name:string){
 const response=await fetch(`${BASE}/api/projects/${projectId}/outputs/${outputId}`);
 if(!response.ok)throw new ApiError('Output unavailable. Refresh the project and try again.',response.status);
 const url=URL.createObjectURL(await response.blob());const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
