import type {Metadata} from 'next';
import Link from 'next/link';
import {Layers3} from 'lucide-react';
import './globals.css';
export const metadata:Metadata={title:'Foundation Depth Automation',description:'Drawing evidence, deterministic calculations and engineering review.'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="en"><body><a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-white focus:p-3">Skip to content</a><header className="border-b border-slate-200 bg-white"><div className="mx-auto flex max-w-[1600px] flex-wrap items-center justify-between gap-3 px-5 py-5 lg:px-10"><Link href="/" className="flex items-center gap-3 font-semibold"><span className="rounded-lg bg-teal-800 p-2 text-white"><Layers3 size={22}/></span>Foundation Depth Automation</Link><div className="flex items-center gap-5 text-sm"><Link href="/" className="text-slate-600 hover:text-teal-800">Projects</Link><span className="badge border-slate-200 text-slate-500">Local engineering MVP</span></div></div></header><main id="main" className="mx-auto max-w-[1600px] px-5 py-8 lg:px-10">{children}</main></body></html>}
