import React, { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import { useStore } from '../store/useStore';
import { SimulationEvent } from '../types';
import {
  Play,
  Pause,
  RotateCcw,
  FastForward,
  Activity,
  Layers,
  Clock,
  UserCheck,
  AlertCircle,
  HelpCircle,
} from 'lucide-react';

interface StageState {
  id: string;
  label: string;
  resourceName: string;
  activeCount: number;
  capacity: number;
  queueLength: number;
  color: string;
}

export const DigitalTwinSimulator: React.FC = () => {
  const { activeSimulationId, setActiveSimulation, selectedProfileId } = useStore();
  const [events, setEvents] = useState<SimulationEvent[]>([]);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [currentTimeMin, setCurrentTimeMin] = useState<number>(0);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(2); // 1x, 2x, 5x, 10x
  const [eventIndex, setEventIndex] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(false);
  
  // Track active stage allocations
  const [stageCounts, setStageCounts] = useState<Record<string, { active: number; queue: number }>>({
    REGISTRATION: { active: 2, queue: 1 },
    TRIAGE: { active: 3, queue: 2 },
    WAITING_FOR_BED: { active: 0, queue: 5 },
    ASSESSMENT: { active: 6, queue: 2 },
    DIAGNOSTICS: { active: 3, queue: 4 },
    TREATMENT: { active: 18, queue: 3 },
    OBSERVATION: { active: 4, queue: 0 },
  });

  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize or fetch events
  useEffect(() => {
    async function loadEvents() {
      setLoading(true);
      try {
        let simId = activeSimulationId;
        if (!simId) {
          // Trigger a baseline simulation run if none exists yet
          const newRun = await api.runSimulation({
            hospital_profile_id: selectedProfileId,
            duration_hours: 24,
            replications: 1,
            random_seed: 42,
          });
          simId = newRun.id;
          setActiveSimulation(newRun.id, newRun.summary_metrics, newRun.bottlenecks);
        }
        const evts = await api.getSimulationEvents(simId, 800);
        setEvents(evts);
        setLoading(false);
      } catch (err) {
        console.error('Failed to load simulation events:', err);
        setLoading(false);
      }
    }
    loadEvents();
  }, [activeSimulationId, selectedProfileId]);

  // Playback timer loop
  useEffect(() => {
    if (isPlaying && events.length > 0) {
      timerRef.current = setInterval(() => {
        setEventIndex((prev) => {
          if (prev >= events.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          const nextIdx = prev + 1;
          const curEvt = events[nextIdx];
          if (curEvt) {
            setCurrentTimeMin(curEvt.timestamp_min);
            
            // Update stage counts dynamically from real event stream
            setStageCounts((s) => {
              const updated = { ...s };
              const stg = curEvt.stage;
              if (updated[stg]) {
                if (curEvt.event_type === 'QUEUE_ENTER') {
                  updated[stg].queue = (curEvt.queue_length ?? updated[stg].queue + 1);
                } else if (curEvt.event_type === 'SERVICE_START') {
                  updated[stg].queue = Math.max(0, updated[stg].queue - 1);
                  updated[stg].active += 1;
                } else if (curEvt.event_type === 'SERVICE_COMPLETE' || curEvt.event_type === 'RESOURCE_RELEASE') {
                  updated[stg].active = Math.max(0, updated[stg].active - 1);
                }
              }
              return updated;
            });
          }
          return nextIdx;
        });
      }, 300 / playbackSpeed);
    } else if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, playbackSpeed, events]);

  const handleReset = () => {
    setIsPlaying(false);
    setEventIndex(0);
    setCurrentTimeMin(0);
  };

  const handleStep = () => {
    if (eventIndex < events.length - 1) {
      const nextIdx = eventIndex + 1;
      setEventIndex(nextIdx);
      const curEvt = events[nextIdx];
      if (curEvt) setCurrentTimeMin(curEvt.timestamp_min);
    }
  };

  const stages: StageState[] = [
    { id: 'REGISTRATION', label: '1. Registration', resourceName: '3 Clerks', activeCount: stageCounts.REGISTRATION?.active || 0, capacity: 3, queueLength: stageCounts.REGISTRATION?.queue || 0, color: 'border-teal-500/50 bg-teal-500/10 text-teal-300' },
    { id: 'TRIAGE', label: '2. Triage (ESI 1-5)', resourceName: '3 Triage Nurses', activeCount: stageCounts.TRIAGE?.active || 0, capacity: 3, queueLength: stageCounts.TRIAGE?.queue || 0, color: 'border-cyan-500/50 bg-cyan-500/10 text-cyan-300' },
    { id: 'WAITING_FOR_BED', label: '3. Bed Allocation Queue', resourceName: '32 ED Beds', activeCount: stageCounts.WAITING_FOR_BED?.active || 0, capacity: 32, queueLength: stageCounts.WAITING_FOR_BED?.queue || 0, color: 'border-amber-500/50 bg-amber-500/10 text-amber-300' },
    { id: 'ASSESSMENT', label: '4. Clinical Assessment', resourceName: '8 Physicians', activeCount: stageCounts.ASSESSMENT?.active || 0, capacity: 8, queueLength: stageCounts.ASSESSMENT?.queue || 0, color: 'border-emerald-500/50 bg-emerald-500/10 text-emerald-300' },
    { id: 'DIAGNOSTICS', label: '5. Diagnostic Imaging & Labs', resourceName: '4 Modalities', activeCount: stageCounts.DIAGNOSTICS?.active || 0, capacity: 4, queueLength: stageCounts.DIAGNOSTICS?.queue || 0, color: 'border-indigo-500/50 bg-indigo-500/10 text-indigo-300' },
    { id: 'TREATMENT', label: '6. Treatment & Nursing Care', resourceName: '16 RNs', activeCount: stageCounts.TREATMENT?.active || 0, capacity: 16, queueLength: stageCounts.TREATMENT?.queue || 0, color: 'border-teal-500/50 bg-teal-500/10 text-teal-300' },
    { id: 'OBSERVATION', label: '7. Clinical Observation', resourceName: '10 Obs Beds', activeCount: stageCounts.OBSERVATION?.active || 0, capacity: 10, queueLength: stageCounts.OBSERVATION?.queue || 0, color: 'border-purple-500/50 bg-purple-500/10 text-purple-300' },
  ];

  const currentEvent = events[eventIndex];
  const simHours = Math.floor(currentTimeMin / 60);
  const simMins = Math.floor(currentTimeMin % 60);

  return (
    <div className="space-y-6">
      {/* Title & Playback Controls Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">Digital Twin Operational Canvas</h1>
            <span className="px-2 py-0.5 rounded text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Discrete-Event Execution
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            SimPy state machine animating patient queues, multi-resource contention, and clinical pathway routing.
          </p>
        </div>

        {/* Playback Controls Toolbar */}
        <div className="flex items-center space-x-3 bg-slate-900 p-2 rounded-2xl border border-slate-800 shadow-lg">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-semibold text-xs transition-all shadow-md shadow-teal-600/30"
          >
            {isPlaying ? <Pause className="w-4 h-4 fill-white" /> : <Play className="w-4 h-4 fill-white" />}
            <span>{isPlaying ? 'Pause' : 'Simulate'}</span>
          </button>

          <button
            onClick={handleStep}
            disabled={isPlaying}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors disabled:opacity-40"
            title="Step One Event"
          >
            Step
          </button>

          <button
            onClick={handleReset}
            className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors"
            title="Reset"
          >
            <RotateCcw className="w-4 h-4" />
          </button>

          <div className="h-5 w-px bg-slate-700" />

          {/* Speed Toggles */}
          <div className="flex items-center space-x-1">
            {[1, 2, 5, 10].map((spd) => (
              <button
                key={spd}
                onClick={() => setPlaybackSpeed(spd)}
                className={`px-2 py-1 rounded-lg text-xs font-semibold transition-all ${
                  playbackSpeed === spd
                    ? 'bg-teal-500/20 text-teal-300 border border-teal-500/40'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {spd}x
              </button>
            ))}
          </div>

          <div className="h-5 w-px bg-slate-700" />

          {/* Simulated Time Counter */}
          <div className="flex items-center space-x-2 px-2 text-xs font-mono font-medium text-slate-300">
            <Clock className="w-4 h-4 text-teal-400" />
            <span>T+{String(simHours).padStart(2, '0')}:{String(simMins).padStart(2, '0')} hrs</span>
          </div>
        </div>
      </div>

      {/* Interactive Operational Canvas */}
      <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 backdrop-blur-md shadow-inner relative overflow-hidden">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Clinical Flow Stages</span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
              Active in System: {currentEvent?.active_in_system ?? 28}
            </span>
          </div>

          <div className="flex items-center space-x-4 text-xs">
            <div className="flex items-center space-x-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-rose-500" />
              <span className="text-slate-400">ESI 1-2 (Emergent)</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-amber-400" />
              <span className="text-slate-400">ESI 3 (Urgent)</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <div className="w-2.5 h-2.5 rounded-full bg-teal-400" />
              <span className="text-slate-400">ESI 4-5 (Less/Non-Urgent)</span>
            </div>
          </div>
        </div>

        {/* Stage Nodes Flow Diagram */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-7 gap-4 relative">
          {stages.map((stg) => {
            const isTarget = currentEvent?.stage === stg.id;
            return (
              <div
                key={stg.id}
                className={`p-4 rounded-xl border transition-all relative ${stg.color} ${
                  isTarget ? 'ring-2 ring-teal-400 shadow-lg shadow-teal-500/20 scale-[1.02]' : 'opacity-90'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-xs font-bold tracking-tight text-white truncate">{stg.label}</h3>
                </div>

                <p className="text-[11px] text-slate-400 font-medium">{stg.resourceName}</p>

                {/* Utilization Gauge */}
                <div className="mt-3 p-2 rounded-lg bg-slate-950/60 border border-slate-800/80">
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-slate-400">In Service</span>
                    <span className="font-bold text-white">{stg.activeCount}/{stg.capacity}</span>
                  </div>
                  <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                    <div
                      className="bg-teal-400 h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${Math.min(100, (stg.activeCount / stg.capacity) * 100)}%` }}
                    />
                  </div>
                </div>

                {/* Queue Tag */}
                <div className="mt-3 flex items-center justify-between p-2 rounded-lg bg-slate-950/40 border border-slate-800/60">
                  <span className="text-[11px] text-slate-400">Queue</span>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                    stg.queueLength > 3 ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' : 'bg-slate-800 text-slate-200'
                  }`}>
                    {stg.queueLength} waiting
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Live Simulation Transition Ticker */}
        <div className="mt-6 p-4 rounded-xl bg-slate-950 border border-slate-800/80 flex flex-col md:flex-row md:items-center md:justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="w-2.5 h-2.5 rounded-full bg-teal-400 animate-pulse" />
            <div>
              <p className="text-xs font-semibold text-slate-200">
                Current Event: <span className="text-teal-300 font-mono">{currentEvent?.event_type || 'QUEUE_ENTER'}</span>
              </p>
              <p className="text-[11px] text-slate-400 mt-0.5">
                Patient <span className="font-mono text-slate-200">{currentEvent?.patient_id || 'PT-00042'}</span> (ESI {currentEvent?.priority || 2}) at <span className="text-slate-200 font-medium">{currentEvent?.stage || 'ASSESSMENT'}</span>
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-4 text-xs text-slate-400">
            <span>Recorded Wait: <strong className="text-white">{currentEvent?.wait_time_min ?? 14.5}m</strong></span>
            <span>Progress: <strong className="text-white">{eventIndex} / {events.length || 800}</strong> events</span>
          </div>
        </div>
      </div>
    </div>
  );
};
