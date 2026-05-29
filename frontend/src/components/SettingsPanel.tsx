import { api } from '../services/api';
import { Settings, useAppStore } from '../store/appStore';

export function SettingsPanel() {
  const settings = useAppStore((state) => state.settings);
  const setSettings = useAppStore((state) => state.setSettings);
  if (!settings) return null;
  const patch = async (payload: Partial<Settings>) => {
    const response = await api<{ settings: Settings }>('/settings', { method: 'POST', body: JSON.stringify(payload) });
    setSettings(response.settings);
  };
  return (
    <section className="glass rounded-3xl p-5">
      <h2 className="mb-4 text-lg font-bold">Settings</h2>
      <label className="flex items-center justify-between rounded-2xl bg-white/5 p-4">Auto organize <input type="checkbox" checked={settings.auto_organize} onChange={(e) => patch({ auto_organize: e.target.checked })} /></label>
      <label className="mt-3 flex items-center justify-between rounded-2xl bg-white/5 p-4">Notifications <input type="checkbox" checked={settings.notifications_enabled} onChange={(e) => patch({ notifications_enabled: e.target.checked })} /></label>
      <label className="mt-3 block rounded-2xl bg-white/5 p-4">Large file threshold MB<input className="mt-2 w-full rounded-xl bg-slate-950 px-3 py-2" type="number" value={settings.max_file_size_large_mb} onChange={(e) => patch({ max_file_size_large_mb: Number(e.target.value) })} /></label>
    </section>
  );
}
