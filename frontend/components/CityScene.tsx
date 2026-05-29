"use client";

import { OrbitControls, Stars } from "@react-three/drei";
import { Canvas, ThreeEvent } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";

import { Building, HeatCell } from "../lib/types";

const colors = {
  residential: "#00f5ff",
  commercial: "#ff2df7",
  industrial: "#ff9f1c",
};

function Heatmap({ cells, size }: { cells: HeatCell[]; size: number }) {
  return (
    <group position={[-size / 2, 0.01, -size / 2]}>
      {cells.map((cell) => {
        const quality = Math.max(0, Math.min(1, (cell.accessibility + cell.resources - cell.pollution) / 200));
        const color = new THREE.Color().lerpColors(new THREE.Color("#ff1744"), new THREE.Color("#00e676"), quality);
        return (
          <mesh key={`${cell.x}-${cell.z}`} position={[cell.x + 0.5, 0, cell.z + 0.5]} rotation={[-Math.PI / 2, 0, 0]}>
            <planeGeometry args={[0.92, 0.92]} />
            <meshBasicMaterial color={color} transparent opacity={0.28} />
          </mesh>
        );
      })}
    </group>
  );
}

function Buildings({ buildings, size, onSelect }: { buildings: Building[]; size: number; onSelect: (building: Building) => void }) {
  const meshRef = useRef<THREE.InstancedMesh>(null);
  const matrix = useMemo(() => new THREE.Matrix4(), []);

  useMemo(() => {
    if (!meshRef.current) return;
    buildings.forEach((building, index) => {
      const height = building.building === "industrial" ? 2.8 : building.building === "commercial" ? 2.2 : 1.4;
      matrix.compose(
        new THREE.Vector3(building.x - size / 2 + 0.5, height / 2, building.z - size / 2 + 0.5),
        new THREE.Quaternion(),
        new THREE.Vector3(0.72, height, 0.72),
      );
      meshRef.current?.setMatrixAt(index, matrix);
      meshRef.current?.setColorAt(index, new THREE.Color(colors[building.building]));
    });
    meshRef.current.instanceMatrix.needsUpdate = true;
    if (meshRef.current.instanceColor) meshRef.current.instanceColor.needsUpdate = true;
  }, [buildings, matrix, size]);

  const handleClick = (event: ThreeEvent<MouseEvent>) => {
    event.stopPropagation();
    if (event.instanceId !== undefined && buildings[event.instanceId]) onSelect(buildings[event.instanceId]);
  };

  return (
    <instancedMesh ref={meshRef} args={[undefined, undefined, Math.max(buildings.length, 1)]} onClick={handleClick}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial emissive="#15f4ee" emissiveIntensity={0.45} metalness={0.35} roughness={0.25} />
    </instancedMesh>
  );
}

export default function CityScene({ buildings, heatmap, size, onSelect }: { buildings: Building[]; heatmap: HeatCell[]; size: number; onSelect: (building: Building) => void }) {
  return (
    <Canvas camera={{ position: [24, 24, 24], fov: 48 }} gl={{ antialias: true }}>
      <fog attach="fog" args={["#050018", 18, 72]} />
      <color attach="background" args={["#050018"]} />
      <ambientLight intensity={0.35} />
      <pointLight position={[0, 18, 0]} intensity={180} color="#00f5ff" />
      <pointLight position={[18, 10, -18]} intensity={90} color="#ff2df7" />
      <Stars radius={80} depth={40} count={1600} factor={4} fade speed={1} />
      <gridHelper args={[size, size, "#00f5ff", "#25144f"]} />
      <Heatmap cells={heatmap} size={size} />
      <Buildings buildings={buildings} size={size} onSelect={onSelect} />
      <OrbitControls enableDamping maxPolarAngle={Math.PI / 2.1} />
    </Canvas>
  );
}
