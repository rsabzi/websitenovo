import { useState, useEffect } from 'react';
import { api } from '../services/api';
import { DuplicateGroup, useAppStore } from '../store/appStore';

export function DuplicateManager() {
  const duplicates = useAppStore((state) => state.duplicates);
  const setDuplicates = useAppStore((state) => state.setDuplicates);
  const [selectedHashes, setSelectedHashes] = useState<Set<string>>(new Set());
  const [isScanning, setIsScanning] = useState(false);

  const fetchExisting = async () => {
    const data = await api<DuplicateGroup[]>('/duplicates');
    setDuplicates(data);
  };

  useEffect(() => {
    fetchExisting();
  }, []);

  const scan = async () => {
    const data = await api<DuplicateGroup[]>('/duplicates/scan', { method: 'POST' });
    setDuplicates(data);
    setSelectedHashes(new Set());
  };

  const resolve = async (group: DuplicateGroup, strategy: 'keep_newest' | 'keep_largest' | 'delete') => {
    await api('/duplicates/resolve', {
      method: 'POST',
      body: JSON.stringify({
        files: group.files.map((file) => file.path),
        strategy
      }),
    });
    await fetchExisting();
  };

  const resolveBulk = async (strategy: 'keep_newest' | 'keep_largest') => {
    const selectedGroups = duplicates.filter(g => selectedHashes.has(g.hash));
    for (const group of selectedGroups) {
      await api('/duplicates/resolve', {
        method: 'POST',
        body: JSON.stringify({
          files: group.files.map((file) => file.path),
          strategy
        }),
      });
    }
    setSelectedHashes(new Set());
    await fetchExisting();
  };

  const toggleSelectAll = () => {
    if (selectedHashes.size === duplicates.length) {
      setSelectedHashes(new Set());
    } else {
      setSelectedHashes(new Set(duplicates.map(g => g.hash)));
    }
  };

  const toggleSelect = (hash: string) => {
    const next = new Set(selectedHashes);
    if (next.has(hash)) {
      next.delete(hash);
    } else {
      next.add(hash);
    }
    setSelectedHashes(next);
  };

  return (
    <section className="glass rounded-3xl p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-bold">Duplicate Manager</h2>
        <div className="flex gap-2">
          {selectedHashes.size > 0 && (
            <div className="flex gap-2 animate-in fade-in slide-in-from-right-4">
              <button
                onClick={() => resolveBulk('keep_newest')}
                className="rounded-xl bg-emerald-500/20 px-4 py-2 text-sm font-medium text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/30 transition-colors"
              >
                Keep Newest ({selectedHashes.size})
              </button>
              <button
                onClick={() => resolveBulk('keep_largest')}
                className="rounded-xl bg-blue-500/20 px-4 py-2 text-sm font-medium text-blue-400 border border-blue-500/30 hover:bg-blue-500/30 transition-colors"
              >
                Keep Largest ({selectedHashes.size})
              </button>
            </div>
          )}
          <button onClick={scan} className="rounded-xl bg-cyan-400 px-4 py-2 font-bold text-slate-950 hover:bg-cyan-300 transition-colors">
            Scan
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {duplicates.length > 0 && (
          <div className="flex items-center gap-2 px-2 pb-2">
            <input
              type="checkbox"
              checked={selectedHashes.size === duplicates.length && duplicates.length > 0}
              onChange={toggleSelectAll}
              className="h-4 w-4 rounded border-white/10 bg-white/5 text-cyan-400 focus:ring-cyan-400"
            />
            <span className="text-sm text-slate-400">Select All ({duplicates.length} groups)</span>
          </div>
        )}

        {duplicates.length === 0 && (
          <p className="text-sm text-slate-500 text-center py-10">No duplicate groups found. Try running a scan.</p>
        )}

        {duplicates.map((group) => (
          <div key={group.hash} className={`rounded-2xl border transition-all ${selectedHashes.has(group.hash) ? 'border-cyan-500/50 bg-cyan-500/5' : 'border-white/10 bg-white/5'} p-4`}>
            <div className="mb-2 flex items-start gap-3">
              <input
                type="checkbox"
                checked={selectedHashes.has(group.hash)}
                onChange={() => toggleSelect(group.hash)}
                className="mt-1 h-4 w-4 rounded border-white/10 bg-white/5 text-cyan-400 focus:ring-cyan-400"
              />
              <div className="flex-1">
                <div className="mb-2 flex justify-between">
                  <b>{group.count} exact duplicates</b>
                  <span className="font-mono text-xs text-slate-500">{group.hash.slice(0, 12)}</span>
                </div>
                <div className="space-y-1">
                  {group.files.map((file) => (
                    <div key={file.path} className="group relative flex items-center gap-2">
                      <div className="truncate text-sm text-slate-300 flex-1">
                        <span className="font-medium text-slate-100">{file.name}</span>
                        <span className="mx-2 text-slate-600">·</span>
                        <span className="text-slate-400">{(file.size / 1024).toFixed(1)} KB</span>
                        <span className="mx-2 text-slate-600">·</span>
                        <span className="text-xs text-slate-500">{file.path}</span>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-4 flex gap-2">
                  <button
                    onClick={() => resolve(group, 'keep_newest')}
                    className="rounded-lg bg-white/5 px-3 py-1.5 text-xs font-medium hover:bg-white/10 transition-colors"
                  >
                    Keep newest
                  </button>
                  <button
                    onClick={() => resolve(group, 'keep_largest')}
                    className="rounded-lg bg-white/5 px-3 py-1.5 text-xs font-medium hover:bg-white/10 transition-colors"
                  >
                    Keep largest
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
