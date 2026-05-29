import { useEffect } from 'react';
import { ActivityFeed } from '../components/ActivityFeed';
import { DuplicateManager } from '../components/DuplicateManager';
import { FolderPanel } from '../components/FolderPanel';
import { LogsPage } from '../components/LogsPage';
import { RulesManager } from '../components/RulesManager';
import { SettingsPanel } from '../components/SettingsPanel';
import { Shell } from '../components/Shell';
import { StatCard } from '../components/StatCard';
import { useLiveEvents } from '../hooks/useLiveEvents';
import { api } from '../services/api';
import { Settings, DuplicateGroup, useAppStore } from '../store/appStore';

function Overview() {
  const events = useAppStore((state) => state.events);
  const settings = useAppStore((state) => state.settings);
  const duplicates = useAppStore((state) => state.duplicates);

  return (
    <div className="space-y-6">
      <div><h1 className="neon text-4xl font-black">Autonomous file hygiene, safely.</h1><p className="mt-2 text-slate-400">Monitor, classify, de-duplicate, rollback, and automate from one polished desktop dashboard.</p></div>
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Live Events" value={events.length} accent="text-cyan-300" />
        <StatCard label="Watched Folders" value={settings?.monitored_folders.length ?? 0} accent="text-fuchsia-300" />
        <StatCard label="Duplicate Groups" value={duplicates.length} accent="text-amber-300" />
        <StatCard label="Auto Organize" value={settings?.auto_organize ? 'ON' : 'OFF'} accent="text-emerald-300" />
      </div>
      <div className="grid grid-cols-[1.2fr_.8fr] gap-6"><ActivityFeed /><FolderPanel /></div>
    </div>
  );
}

export default function App() {
  useLiveEvents();
  const activePage = useAppStore((state) => state.activePage);
  const setSettings = useAppStore((state) => state.setSettings);
  const setDuplicates = useAppStore((state) => state.setDuplicates);

  useEffect(() => { 
    api<Settings>('/settings').then(setSettings);
    api<DuplicateGroup[]>('/duplicates').then(setDuplicates);
  }, [setSettings, setDuplicates]);

  // Force environment check at the highest level
  const isElectron = window.navigator.userAgent.toLowerCase().includes('electron');
  if (!isElectron) {
    return (
      <div className="flex h-screen items-center justify-center bg-[#020617] text-white p-10 text-center font-sans">
        <div className="max-w-md p-8 glass rounded-3xl border border-white/10 shadow-2xl">
          <div className="w-16 h-16 bg-cyan-500/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-cyan-400"><rect width="18" height="12" x="3" y="4" rx="2" ry="2"/><line x1="2" x2="22" y1="20" y2="20"/><line x1="12" x2="12" y1="20" y2="16"/></svg>
          </div>
          <h1 className="text-3xl font-black mb-4 neon">Desktop Only</h1>
          <p className="text-slate-400 leading-relaxed mb-6">
            This AI File Organizer requires direct file system access and must be run as a Windows application.
          </p>
          <div className="text-xs text-slate-500 bg-white/5 p-3 rounded-xl border border-white/5">
            Please use the <code className="text-cyan-300">run_app.bat</code> file to launch the desktop version.
          </div>
        </div>
      </div>
    );
  }

  const page = activePage === 'Overview' ? <Overview /> : activePage === 'Folders' ? <FolderPanel /> : activePage === 'Rules' ? <RulesManager /> : activePage === 'Duplicates' ? <DuplicateManager /> : activePage === 'Logs' ? <LogsPage /> : <SettingsPanel />;
  return <Shell>{page}</Shell>;
}
