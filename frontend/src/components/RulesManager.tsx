import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Rule, useAppStore } from '../store/appStore';

export function RulesManager() {
  const rules = useAppStore((state) => state.rules);
  const setRules = useAppStore((state) => state.setRules);
  const [extension, setExtension] = useState('.pdf');
  const [target, setTarget] = useState('Documents');
  useEffect(() => { api<Rule[]>('/rules').then(setRules); }, [setRules]);
  const create = async () => {
    await api<Rule>('/rules', { method: 'POST', body: JSON.stringify({ name: `${extension} → ${target}`, condition: { extension }, action: { type: 'move', move_to: target } }) });
    setRules(await api<Rule[]>('/rules'));
  };
  return (
    <section className="glass rounded-3xl p-5">
      <h2 className="mb-4 text-lg font-bold">Rules Manager</h2>
      <div className="mb-5 grid grid-cols-[1fr_1fr_auto] gap-3">
        <input className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3" value={extension} onChange={(e) => setExtension(e.target.value)} />
        <input className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3" value={target} onChange={(e) => setTarget(e.target.value)} />
        <button onClick={create} className="rounded-2xl bg-cyan-400 px-5 font-bold text-slate-950">Add</button>
      </div>
      <div className="grid gap-3">
        {rules.map((rule) => <div key={rule.id} className="rounded-2xl bg-white/5 p-4"><b>{rule.name}</b><pre className="mt-2 overflow-auto text-xs text-slate-400">{JSON.stringify({ condition: rule.condition, action: rule.action }, null, 2)}</pre></div>)}
      </div>
    </section>
  );
}
