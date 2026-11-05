import React, { useState } from 'react';
import { api } from '../services/api';
import { useStore } from '../store/useStore';
import { SimulationResults, Bottleneck } from '../types';
import {
  Sliders,
  Play,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Bed,
  Users,
  Activity,
  Zap,
  ArrowRight,
  TrendingUp,
} from 'lucide-react';

export const ScenarioLab: React.FC = () => {
  const { setActiveSimulation, setCurrentPage, selectedProfileId } = useStore();

  const [surgePct, setSurgePct] = useState<number>(40);
  const [physicianCount, setPhysicianCount] = useState<number>(8);
  const [nurseCount, setNurseCount] = useState<number>(16);
  const [bedCount, setBedCount] = useState<number>(32);
  const [diagCount, setDiagCount] = useState<number>(4);
  const [durationHours, setDurationHours] = useState<number>(48);
  const [replications, setReplications] = useState<number>(5);
  const [seed, setSeed] = useState<number>(42);

  const [loading, setLoading] = useState<boolean>(false);
  const [results, setResults] = useState<SimulationResults | null>(null);
  const [bottlenecks, setBottlenecks] = useState<Bottleneck[]>([]);

  const presets = [
    { name: 'Baseline Normal', surge: 0, md: 8, rn: 16, beds: 32, diag: 4, desc: 'Nominal operational staffing under standard diurnal load.' },
    { name: 'Scenario A: Sudden Surge (+40%)', surge: 40, md: 8, rn: 16, beds: 32, diag: 4, desc: 'Sudden 40% influx simulating community outbreak.' },
    { name: 'Scenario B: Nurse Shortage (-20%)', surge: 0, md: 8, rn: 12, beds: 32, diag: 4, desc: 'Unexpected nursing absenteeism creating treatment delays.' },
    { name: 'Scenario C: Bed Closure (-5 Beds)', surge: 0, md: 8, rn: 16, beds: 27, diag: 4, desc: 'Temporary bed closures for sanitization/maintenance.' },
    { name: 'Scenario E: Diagnostic Outage (-2 Units)', surge: 0, md: 8, rn: 16, beds: 32, diag: 2, desc: '50% loss of CT/X-Ray imaging stations.' },
    { name: 'Scenario G: Severe Compound Crisis', surge: 30, md: 6, rn: 12, beds: 26, diag: 3, desc: 'Combined surge + staffing shortage + bed outage.' },
  ];

  const applyPreset = (p: typeof presets[0]) => {
    setSurgePct(p.surge);
    setPhysicianCount(p.md);
    setNurseCount(p.rn);
    setBedCount(p.beds);
    setDiagCount(p.diag);
  };

  const handleRunSimulation = async () => {
    setLoading(true);
    try {
      const res = await api.runSimulation({
        hospital_profile_id: selectedProfileId,
        arrival_surge_pct: surgePct,
        physician_count: physicianCount,
        nurse_count: nurseCount,
        bed_count: bedCount,
        diagnostic_count: diagCount,
        duration_hours: durationHours,
        replications: replications,
        random_seed: seed,
      });

      setResults(res.summary_metrics);
      setBottlenecks(res.bottlenecks || []);
      setActiveSimulation(res.id, res.summary_metrics, res.bottlenecks || []);
      setLoading(false);
    } catch (err) {
      console.error('Failed to run simulation:', err);
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">What-If Scenario Laboratory</h1>
            <span className="px-2 py-0.5 rounded text-xs font-semibold bg-teal-500/20 text-teal-400 border border-teal-500/30">
              Interactive Digital Twin
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Induce surges, staffing shortages, and capacity bottlenecks to measure downstream impacts in genuine SimPy discrete events.
          </p>
        </div>

        <button
          onClick={handleRunSimulation}
          disabled={loading}
          className="flex items-center justify-center space-x-2 px-6 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 disabled:opacity-50 text-white font-semibold text-sm transition-all shadow-lg shadow-teal-600/30"
        >
          {loading ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <Play className="w-4 h-4 fill-white" />
          )}
          <span>{loading ? 'Simulating Replications...' : 'Execute Digital Twin Simulation'}</span>
        </button>
      </div>

      {/* Preset Quick Selectors */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
        {presets.map((p, idx) => (
          <button
            key={idx}
            onClick={() => applyPreset(p)}
            className="p-3 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-teal-500/50 text-left transition-all"
          >
            <p className="text-xs font-bold text-white truncate">{p.name}</p>
            <p className="text-[10px] text-slate-400 mt-1 line-clamp-2 leading-tight">{p.desc}</p>
          </button>
        ))}
      </div>

      {/* Interactive Controls & Parameters Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sliders Configuration Column */}
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-5">
          <h2 className="text-base font-bold text-white flex items-center space-x-2">
            <Sliders className="w-5 h-5 text-teal-400" />
            <span>Scenario Stress Parameters</span>
          </h2>

          {/* Surge % */}
          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-slate-300 font-medium">Arrival Surge Intensity</span>
              <span className="font-mono font-bold text-teal-300">{surgePct > 0 ? `+${surgePct}%` : `${surgePct}%`}</span>
            </div>
            <input
              type="range"
              min="-20"
              max="100"
              step="5"
              value={surgePct}
              onChange={(e) => setSurgePct(Number(e.target.value))}
              className="w-full accent-teal-500 bg-slate-800 rounded-lg cursor-pointer"
            />
          </div>

          {/* Physicians */}
          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-slate-300 font-medium">Attending Physicians</span>
              <span className="font-mono font-bold text-teal-300">{physicianCount} MDs</span>
            </div>
            <input
              type="range"
              min="2"
              max="20"
              value={physicianCount}
              onChange={(e) => setPhysicianCount(Number(e.target.value))}
              className="w-full accent-teal-500 bg-slate-800 rounded-lg cursor-pointer"
            />
          </div>

          {/* Nurses */}
          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-slate-300 font-medium">Registered Nurses</span>
              <span className="font-mono font-bold text-teal-300">{nurseCount} RNs</span>
            </div>
            <input
              type="range"
              min="4"
              max="40"
              value={nurseCount}
              onChange={(e) => setNurseCount(Number(e.target.value))}
              className="w-full accent-teal-500 bg-slate-800 rounded-lg cursor-pointer"
            />
          </div>

          {/* Beds */}
          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-slate-300 font-medium">Treatment Beds</span>
              <span className="font-mono font-bold text-teal-300">{bedCount} Beds</span>
            </div>
            <input
              type="range"
              min="10"
              max="60"
              value={bedCount}
              onChange={(e) => setBedCount(Number(e.target.value))}
              className="w-full accent-teal-500 bg-slate-800 rounded-lg cursor-pointer"
            />
          </div>

          {/* Diagnostics */}
          <div>
            <div className="flex justify-between text-xs mb-1.5">
              <span className="text-slate-300 font-medium">Diagnostic Stations (CT/X-Ray)</span>
              <span className="font-mono font-bold text-teal-300">{diagCount} Stations</span>
            </div>
            <input
              type="range"
              min="1"
              max="8"
              value={diagCount}
              onChange={(e) => setDiagCount(Number(e.target.value))}
              className="w-full accent-teal-500 bg-slate-800 rounded-lg cursor-pointer"
            />
          </div>

          {/* Duration & Seeds */}
          <div className="grid grid-cols-2 gap-3 pt-2 border-t border-slate-800">
            <div>
              <span className="text-[11px] text-slate-400">Duration (Hours)</span>
              <select
                value={durationHours}
                onChange={(e) => setDurationHours(Number(e.target.value))}
                className="w-full mt-1 p-2 bg-slate-800 text-xs rounded-lg text-slate-200 border border-slate-700 outline-none"
              >
                <option value={12}>12 Hours</option>
                <option value={24}>24 Hours</option>
                <option value={48}>48 Hours</option>
                <option value={72}>72 Hours</option>
              </select>
            </div>
            <div>
              <span className="text-[11px] text-slate-400">Monte Carlo Replications</span>
              <select
                value={replications}
                onChange={(e) => setReplications(Number(e.target.value))}
                className="w-full mt-1 p-2 bg-slate-800 text-xs rounded-lg text-slate-200 border border-slate-700 outline-none"
              >
                <option value={1}>1 (Deterministic Trace)</option>
                <option value={3}>3 (Fast Stochastic)</option>
                <option value={5}>5 (Standard 95% CI)</option>
                <option value={10}>10 (Publication Grade)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Results & Statistical Diagnostics Column */}
        <div className="lg:col-span-2 space-y-6">
          {results ? (
            <>
              {/* Top Summary Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-xs text-slate-400">Mean Wait Time</span>
                  <p className="text-2xl font-extrabold text-white mt-1">{results.mean_wait_time.mean}m</p>
                  <span className="text-[10px] text-slate-500">95% CI: [{results.mean_wait_time.ci_lower}m, {results.mean_wait_time.ci_upper}m]</span>
                </div>

                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-xs text-slate-400">P95 Wait Time</span>
                  <p className={`text-2xl font-extrabold mt-1 ${results.p95_wait_time.mean > 90 ? 'text-rose-400' : 'text-teal-300'}`}>
                    {results.p95_wait_time.mean}m
                  </p>
                  <span className="text-[10px] text-slate-500">worst-case tail delay</span>
                </div>

                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-xs text-slate-400">Hourly Throughput</span>
                  <p className="text-2xl font-extrabold text-white mt-1">{results.throughput_per_hour.mean}</p>
                  <span className="text-[10px] text-slate-500">departures / hour</span>
                </div>

                <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
                  <span className="text-xs text-slate-400">Average LOS</span>
                  <p className="text-2xl font-extrabold text-white mt-1">{results.mean_los.mean}m</p>
                  <span className="text-[10px] text-slate-500">length of stay</span>
                </div>
              </div>

              {/* Resource Utilization Table */}
              <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
                <h3 className="text-sm font-bold text-white mb-3 flex items-center justify-between">
                  <span>Resource Utilization Breakdown</span>
                  <span className="text-xs text-slate-400 font-normal">Conservation Verified: {results.conservation_verified ? 'Yes (Zero Discrepancy)' : 'No'}</span>
                </h3>

                <div className="space-y-3">
                  {Object.entries(results.resource_utilization).map(([resKey, util]) => (
                    <div key={resKey}>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-300 capitalize">{resKey.replace('_', ' ')}</span>
                        <span className={`font-mono font-bold ${util.mean_pct > 80 ? 'text-rose-400' : 'text-slate-200'}`}>
                          {util.mean_pct}% <span className="text-[10px] text-slate-500 font-normal">[{util.ci_lower}%, {util.ci_upper}%]</span>
                        </span>
                      </div>
                      <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div
                          className={`h-1.5 rounded-full ${util.mean_pct > 80 ? 'bg-rose-500' : 'bg-teal-500'}`}
                          style={{ width: `${Math.min(100, util.mean_pct)}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Bottleneck Alerts */}
              {bottlenecks.length > 0 && (
                <div className="p-5 rounded-2xl bg-amber-500/10 border border-amber-500/20 space-y-3">
                  <h3 className="text-sm font-bold text-amber-300 flex items-center space-x-2">
                    <AlertTriangle className="w-4 h-4 text-amber-400" />
                    <span>Identified Operational Bottlenecks ({bottlenecks.length})</span>
                  </h3>
                  {bottlenecks.map((b, i) => (
                    <div key={i} className="text-xs text-amber-200/90 flex items-start space-x-2">
                      <div className="w-1.5 h-1.5 rounded-full bg-amber-400 mt-1.5 flex-shrink-0" />
                      <div>
                        <strong>{b.resource.replace('_', ' ').toUpperCase()}:</strong> {b.recommendation}
                        <span className="text-teal-300 ml-1">Estimated counterfactual wait reduction: -{b.counterfactual_wait_reduction_min}m</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          ) : (
            <div className="p-12 rounded-2xl bg-slate-900/50 border border-dashed border-slate-800 flex flex-col items-center justify-center text-center">
              <Zap className="w-10 h-10 text-teal-400/60 mb-3" />
              <h3 className="text-base font-bold text-white">Simulation Engine Ready</h3>
              <p className="text-xs text-slate-400 max-w-sm mt-1">
                Configure stress parameters or select a scenario preset, then click &ldquo;Execute Digital Twin Simulation&rdquo; to compute multi-replication queue metrics.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
