import { AnimatePresence, motion } from 'framer-motion';
import { Archive, Bot, Copy, FileClock, FolderSearch, LayoutDashboard, ListFilter, Settings } from 'lucide-react';
import { useAppStore } from '../store/appStore';

const nav = [
  ['Overview', LayoutDashboard],
  ['Folders', FolderSearch],
  ['Rules', ListFilter],
  ['Duplicates', Copy],
  ['Logs', FileClock],
  ['Settings', Settings],
] as const;

export function Shell({ children }: { children: React.ReactNode }) {
  const activePage = useAppStore((state) => state.activePage);
  const setPage = useAppStore((state) => state.setPage);
  return (
    <div className="min-h-screen overflow-hidden bg-[radial-gradient(circle_at_top_left,#0e7490_0,transparent_26%),radial-gradient(circle_at_bottom_right,#7c3aed_0,transparent_30%),#020617]">
      <div className="grid min-h-screen grid-cols-[280px_1fr] gap-6 p-6">
        <aside className="glass rounded-3xl p-5">
          <div className="mb-8 flex items-center gap-3">
            <div className="rounded-2xl bg-cyan-400/15 p-3 text-cyan-300"><Bot /></div>
            <div><h1 className="neon text-xl font-black">AI File Organizer</h1><p className="text-xs text-slate-400">Desktop automation agent</p></div>
          </div>
          <nav className="space-y-2">
            {nav.map(([label, Icon]) => (
              <button key={label} onClick={() => setPage(label)} className={`flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left transition ${activePage === label ? 'bg-cyan-400/15 text-cyan-200' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}>
                <Icon size={18} /> {label}
              </button>
            ))}
          </nav>
          <div className="mt-8 rounded-3xl border border-fuchsia-400/20 bg-fuchsia-400/10 p-4 text-sm text-fuchsia-100">
            <Archive className="mb-2" size={18} /> Safe moves, rollback history, duplicate protection, local-first AI suggestions.
          </div>
        </aside>
        <main className="min-w-0">
          <AnimatePresence mode="wait">
            <motion.div key={activePage} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }} transition={{ duration: 0.22 }}>
              {children}
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  );
}
