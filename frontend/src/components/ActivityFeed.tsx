import { useAppStore } from '../store/appStore';

export function ActivityFeed() {
  const events = useAppStore((state) => state.events);
  return (
    <section className="glass rounded-3xl p-5">
      <div className="mb-4 flex items-center justify-between"><h2 className="text-lg font-bold">Live Activity</h2><span className="text-xs text-cyan-300">WebSocket</span></div>
      <div className="max-h-[420px] space-y-3 overflow-auto pr-2">
        {events.length === 0 && <p className="text-sm text-slate-500">Waiting for file events...</p>}
        {events.map((event, index) => (
          <div key={`${event.timestamp}-${index}`} className="rounded-2xl border border-white/10 bg-white/[0.03] p-3">
            <div className="flex items-center justify-between"><b className="text-cyan-200">{event.type}</b><span className="text-xs text-slate-500">{new Date(event.timestamp).toLocaleTimeString()}</span></div>
            <p className="truncate text-sm text-slate-300">{event.filename ?? event.path ?? event.rule ?? 'system event'}</p>
            {event.to && <p className="truncate text-xs text-slate-500">→ {event.to}</p>}
          </div>
        ))}
      </div>
    </section>
  );
}
