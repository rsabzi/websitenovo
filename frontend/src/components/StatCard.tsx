import { motion } from 'framer-motion';
import { panel } from '../animations/variants';

export function StatCard({ label, value, accent }: { label: string; value: string | number; accent: string }) {
  return (
    <motion.div variants={panel} initial="hidden" animate="visible" className="glass rounded-3xl p-5">
      <p className="text-sm text-slate-400">{label}</p>
      <motion.div className={`mt-2 text-4xl font-black ${accent}`} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>{value}</motion.div>
    </motion.div>
  );
}
