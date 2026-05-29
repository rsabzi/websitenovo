import { FolderPlus } from 'lucide-react';
import { api } from '../services/api';
import { useAppStore } from '../store/appStore';

declare global { interface Window { desktop?: { selectFolder: () => Promise<string[]> } } }

export function FolderPanel() {
  const settings = useAppStore((state) => state.settings);
  const setSettings = useAppStore((state) => state.setSettings);
  const addFolder = async () => {
    const folders = await window.desktop?.selectFolder?.();
    for (const folder of folders ?? []) {
      const response = await api<{ settings: typeof settings }>('/folders?folder=' + encodeURIComponent(folder), { method: 'POST' });
      if (response.settings) setSettings(response.settings);
    }
  };
  return (
    <section className="glass rounded-3xl p-5">
      <div className="mb-4 flex items-center justify-between"><h2 className="text-lg font-bold">Folder Monitor</h2><button onClick={addFolder} className="rounded-xl bg-cyan-400 px-3 py-2 text-sm font-bold text-slate-950"><FolderPlus size={16} /></button></div>
      <div className="space-y-2">
        {settings?.monitored_folders.length ? settings.monitored_folders.map((folder) => <div className="truncate rounded-2xl bg-white/5 p-3 text-sm" key={folder}>{folder}</div>) : <p className="text-sm text-slate-500">No monitored folders yet.</p>}
      </div>
    </section>
  );
}
