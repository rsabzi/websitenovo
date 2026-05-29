"use client";

import { Building, Metrics } from "../lib/types";

export default function Dashboard({ metrics, selected }: { metrics: Metrics | null; selected: Building | null }) {
  return (
    <aside className="panel">
      <div className="brand">Neural City Architect</div>
      <p className="subtitle">Bounded multi-agent city growth with safe meta-optimization.</p>
      <div className="metrics">
        <span>Tick <b>{metrics?.tick ?? 0}</b></span>
        <span>Buildings <b>{metrics?.building_count ?? 0}</b></span>
        <span>Avg Score <b>{metrics?.average_score ?? 0}</b></span>
        <span>Pollution <b>{metrics?.average_pollution ?? 0}</b></span>
      </div>
      <h3>Selected Building</h3>
      {selected ? (
        <div className="card hot">
          <b>{selected.building.toUpperCase()}</b>
          <span>Score: {selected.score}</span>
          <span>Agent: {selected.agent}</span>
          <p>{selected.reason}</p>
        </div>
      ) : (
        <div className="card">Click a neon tower to inspect the agent decision.</div>
      )}
      <h3>Resources</h3>
      <div className="card gridTwo">
        <span>Power</span><b>{metrics?.resources.power ?? 0}</b>
        <span>Water</span><b>{metrics?.resources.water ?? 0}</b>
        <span>Road</span><b>{metrics?.resources.road_access ?? 0}</b>
      </div>
      <h3>Meta Optimizer</h3>
      <div className="card">{metrics?.meta?.suggestion ?? "Waiting for the next safe optimization window."}</div>
      <h3>Agent Logs</h3>
      <div className="logs">
        {(metrics?.logs ?? []).slice().reverse().map((log) => <code key={log}>{log}</code>)}
      </div>
    </aside>
  );
}
