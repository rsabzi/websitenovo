"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import Dashboard from "../components/Dashboard";
import { fetchJson, websocketUrl } from "../lib/api";
import { Building, HeatCell, Metrics } from "../lib/types";

const CityScene = dynamic(() => import("../components/CityScene"), { ssr: false });

export default function Home() {
  const [size, setSize] = useState(32);
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [heatmap, setHeatmap] = useState<HeatCell[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [selected, setSelected] = useState<Building | null>(null);

  useEffect(() => {
    fetchJson<{ size: number; buildings: Building[]; heatmap: HeatCell[] }>("/grid").then((grid) => {
      setSize(grid.size);
      setBuildings(grid.buildings);
      setHeatmap(grid.heatmap);
    });
    fetchJson<Metrics>("/metrics").then(setMetrics);

    const ws = new WebSocket(websocketUrl());
    ws.onmessage = (message) => {
      const event = JSON.parse(message.data);
      if (event.type === "SNAPSHOT") {
        setSize(event.grid.size);
        setBuildings(event.grid.buildings);
        setHeatmap(event.grid.heatmap);
        setMetrics(event.metrics);
      }
      if (event.type === "BUILD") {
        const nextBuilding: Building = {
          id: event.id,
          x: event.x,
          z: event.z,
          building: event.building,
          score: event.score,
          agent: event.agent,
          reason: event.reason,
          tick: event.tick,
        };
        setBuildings((current) => [...current, nextBuilding]);
        setMetrics(event.metrics);
      }
    };
    return () => ws.close();
  }, []);

  return (
    <main className="shell">
      <section className="viewport">
        <CityScene buildings={buildings} heatmap={heatmap} size={size} onSelect={setSelected} />
        <div className="legend"><span className="green" /> good cells <span className="red" /> risky cells</div>
      </section>
      <Dashboard metrics={metrics} selected={selected} />
    </main>
  );
}
