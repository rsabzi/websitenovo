import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { LogRecord, useAppStore } from '../store/appStore';

export function LogsPage() {
  const logs = useAppStore((state) => state.logs);
  const setLogs = useAppStore((state) => state.setLogs);
  const [query, setQuery] = useState('');
  const load = () => api<LogRecord[]>('/logs' + (query ? `?query=${encodeURIComponent(query)}` : '')).then(setLogs);
  useEffect(load, [setLogs]);
  return (
    <section className="glass rounded-3xl p-5">
      <div className="mb-4 flex gap-3"><input className="flex-1 rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3" placeholder="Search logs" value={query} onChange={(e) => setQuery(e.target.value)} /><button onClick={load} className="rounded-2xl bg-cyan-400 px-5 font-bold text-slate-950">Search</button></div>
      <div className="max-h-[640px] space-y-3 overflow-auto">{logs.map((log, index) => <div key={`${log.timestamp}-${index}`} className="rounded-2xl bg-white/5 p-4"><b className="text-cyan-200">{log.type}</b><p>{log.message}</p><span className="text-xs text-slate-500">{new Date(log.timestamp).toLocaleString()}</span></div>)}</div>
    </section>
  );
}
