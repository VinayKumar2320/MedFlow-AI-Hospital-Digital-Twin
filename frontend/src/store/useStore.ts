import { create } from 'zustand';
import { SimulationResults, SimulationEvent, OptimizationResponse, Bottleneck } from '../types';

export type PageId =
  | 'command_center'
  | 'forecasting'
  | 'digital_twin'
  | 'scenario_lab'
  | 'optimization'
  | 'comparison'
  | 'model_intelligence';

interface AppState {
  currentPage: PageId;
  setCurrentPage: (page: PageId) => void;
  
  selectedProfileId: string;
  setSelectedProfileId: (id: string) => void;
  
  // Active Simulation
  activeSimulationId: string | null;
  activeSimulationResults: SimulationResults | null;
  activeSimulationBottlenecks: Bottleneck[];
  simulationEvents: SimulationEvent[];
  setActiveSimulation: (id: string, results: SimulationResults, bottlenecks: Bottleneck[]) => void;
  setSimulationEvents: (events: SimulationEvent[]) => void;
  
  // Active Optimization
  activeOptimization: OptimizationResponse | null;
  setActiveOptimization: (opt: OptimizationResponse) => void;
  
  // What-If Scenario State
  surgePct: number;
  setSurgePct: (val: number) => void;
  physicianDelta: number;
  setPhysicianDelta: (val: number) => void;
  nurseDelta: number;
  setNurseDelta: (val: number) => void;
  bedDelta: number;
  setBedDelta: (val: number) => void;
  diagnosticDelta: number;
  setDiagnosticDelta: (val: number) => void;
}

export const useStore = create<AppState>((set) => ({
  currentPage: 'command_center',
  setCurrentPage: (page) => set({ currentPage: page }),
  
  selectedProfileId: 'urban',
  setSelectedProfileId: (id) => set({ selectedProfileId: id }),
  
  activeSimulationId: null,
  activeSimulationResults: null,
  activeSimulationBottlenecks: [],
  simulationEvents: [],
  setActiveSimulation: (id, results, bottlenecks) =>
    set({ activeSimulationId: id, activeSimulationResults: results, activeSimulationBottlenecks: bottlenecks }),
  setSimulationEvents: (events) => set({ simulationEvents: events }),
  
  activeOptimization: null,
  setActiveOptimization: (opt) => set({ activeOptimization: opt }),
  
  surgePct: 0,
  setSurgePct: (val) => set({ surgePct: val }),
  physicianDelta: 0,
  setPhysicianDelta: (val) => set({ physicianDelta: val }),
  nurseDelta: 0,
  setNurseDelta: (val) => set({ nurseDelta: val }),
  bedDelta: 0,
  setBedDelta: (val) => set({ bedDelta: val }),
  diagnosticDelta: 0,
  setDiagnosticDelta: (val) => set({ diagnosticDelta: val }),
}));
