import {clsx,type ClassValue} from 'clsx';
import {twMerge} from 'tailwind-merge';
export function cn(...inputs:ClassValue[]){return twMerge(clsx(inputs));}
export function label(value:string){return value.replaceAll('_',' ');}
export function bytes(value:number){return value>=1048576?`${(value/1048576).toFixed(1)} MiB`:`${Math.ceil(value/1024)} KiB`;}
