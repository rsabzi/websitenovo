export type BuildingType = "residential" | "commercial" | "industrial";

export type Building = {
  id: number;
  x: number;
  z: number;
  building: BuildingType;
  score: number;
  agent: string;
  reason: string;
  tick: number;
};

export type HeatCell = {
  x: number;
  z: number;
  accessibility: number;
  resources: number;
  pollution: number;
};

export type Metrics = {
  tick: number;
  building_count: number;
  average_score: number;
  average_pollution: number;
  resources: { power: number; water: number; road_access: number };
  weights: { accessibility: number; resources: number; pollution: number };
  logs: string[];
  meta?: { suggestion: string; new_weights: Record<string, number>; suggested_agent_types: string[] } | null;
};
