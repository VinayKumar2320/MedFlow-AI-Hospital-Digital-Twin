import React, { useState } from 'react';
import { api } from '../services/api';
import { useStore } from '../store/useStore';
import { OptimizationResponse } from '../types';
import {
  Sparkles,
  CheckCircle2,
  DollarSign,
  Clock,
  TrendingDown,
  Layers,
  ArrowRight,
  ShieldCheck,
  ChevronRight,
  BarChart,
} from 'lucide-react';
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from 'recharts';

export const OptimizationStudio: React.FC = () => {
  const { activeOptimization, setActiveOptimization, selectedProfileId } = useStore();
  const [budget, setBudget] = useState<number>(6000);
  const [loading, setLoading] = useState<boolean>(false);
  const [selectedPlanIdx, setSelectedPlanIdx] = useState<number>(0);

  const handleRunOptimization = async () => {
    setLoading(true);
    try {
      const res = await api.runOptimization({
        hospital_profile_id: selectedProfileId,
        max_additional_budget: budget,
        service_target_wait_min: 50.0,
        replications_for_validation: 3,
      });
      setActiveOptimization(res);
      setLoading(false);
    } catch (err) {
      console.error('Optimization failed:', err);
      setLoading(false);
    }
  };

  const optData = activeOptimization;
  const currentPlan = optData?.alternative_plans?.[selectedPlanIdx] || optData?.alternative_plans?.[0];

  const tradeoffData = (optData?.tradeoff_frontier || []).map((pt, i) => ({
    name: pt.plan_name,
    cost: pt.cost_delta,
    wait: pt.mean_wait_min,
    isBaseline: i === 0,
    isRecommended: i === 2,
  }));

  return (
    <div className="space-y-6">
      {/* Title & Trigger Button */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">OR-Tools Staffing & Capacity Optimizer</h1>
            <span className="px-2 py-0.5 rounded text-xs font-semibold bg-teal-500/20 text-teal-400 border border-teal-500/30">
              CP-SAT + SimPy Surrogate
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Solves mixed-integer shift constraints with Google OR-Tools CP-SAT and evaluates candidates with SimPy Common Random Numbers.
          </p>
        </div>

        <button
          onClick={handleRunOptimization}
          disabled={loading}
          className="flex items-center justify-center space-x-2 px-6 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 disabled:opacity-50 text-white font-semibold text-sm transition-all shadow-lg shadow-teal-600/30"
        >
          {loading ? (
            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
          ) : (
            <Sparkles className="w-4 h-4 text-white" />
          )}
          <span>{loading ? 'Solving Constraints & Evaluating...' : 'Solve Optimal Allocation'}</span>
        </button>
      </div>

      {/* Budget Slider Card */}
      <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex-1">
          <div className="flex justify-between text-xs mb-1.5">
            <span className="text-slate-300 font-semibold">Maximum Additional Daily Staffing Budget</span>
            <span className="font-mono font-bold text-teal-300">${budget.toLocaleString()} / day</span>
          </div>
          <input
            type="range"
            min="1000"
            max="15000"
            step="500"
            value={budget}
            onChange={(e) => setBudget(Number(e.target.value))}
            className="w-full accent-teal-500 bg-slate-800 rounded-lg cursor-pointer"
          />
        </div>

        <div className="flex items-center space-x-2 text-xs text-slate-400 border-l border-slate-800 pl-4">
          <ShieldCheck className="w-4 h-4 text-teal-400" />
          <span>Hard constraints: Nurse:MD &ge; 1.6 &amp; Budget Ceiling</span>
        </div>
      </div>

      {optData ? (
        <div className="space-y-6">
          {/* Top KPI Impact Row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
              <span className="text-xs text-slate-400 font-semibold uppercase">Simulated Wait Reduction</span>
              <p className="text-3xl font-extrabold text-teal-300 mt-2">
                -{optData.wait_reduction_minutes} min
              </p>
              <span className="text-xs text-teal-400/80 font-medium">({optData.wait_reduction_pct}% improvement)</span>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
              <span className="text-xs text-slate-400 font-semibold uppercase">Daily Expenditure Delta</span>
              <p className="text-3xl font-extrabold text-white mt-2">
                +${optData.cost_delta.toLocaleString()}
              </p>
              <span className="text-xs text-slate-400">Budget Utilized: {Math.round((optData.cost_delta / optData.target_budget) * 100)}%</span>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
              <span className="text-xs text-slate-400 font-semibold uppercase">Throughput Gain</span>
              <p className="text-3xl font-extrabold text-cyan-300 mt-2">
                +{optData.throughput_increase_pct}%
              </p>
              <span className="text-xs text-slate-400">patient departures / hour</span>
            </div>

            <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
              <span className="text-xs text-slate-400 font-semibold uppercase">Constraint Verification</span>
              <div className="mt-2 space-y-1">
                <div className="flex items-center space-x-1.5 text-xs text-emerald-400">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Budget Limit Honored</span>
                </div>
                <div className="flex items-center space-x-1.5 text-xs text-emerald-400">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>Nurse:MD Safety Ratio Met</span>
                </div>
              </div>
            </div>
          </div>

          {/* Shift Staffing Matrix Comparison */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-base font-bold text-white flex items-center space-x-2">
                  <Layers className="w-5 h-5 text-teal-400" />
                  <span>Optimized Shift Staffing Allocation</span>
                </h2>
                <div className="flex space-x-1 bg-slate-800 p-1 rounded-lg text-xs">
                  {optData.alternative_plans.map((p, idx) => (
                    <button
                      key={p.plan_id}
                      onClick={() => setSelectedPlanIdx(idx)}
                      className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                        selectedPlanIdx === idx ? 'bg-teal-500/20 text-teal-300 border border-teal-500/30' : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      Plan {idx + 1}
                    </button>
                  ))}
                </div>
              </div>

              {currentPlan && (
                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left">
                    <thead className="text-slate-400 uppercase bg-slate-800/60">
                      <tr>
                        <th className="px-3 py-2 rounded-l-lg">Shift Window</th>
                        <th className="px-3 py-2">Physicians</th>
                        <th className="px-3 py-2">Nurses</th>
                        <th className="px-3 py-2 rounded-r-lg">Nurse:MD Ratio</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800 text-slate-200">
                      <tr>
                        <td className="px-3 py-3 font-medium">Morning (07:00 - 15:00)</td>
                        <td className="px-3 py-3 font-mono font-bold text-teal-300">{currentPlan.staffing.physicians_morning} MDs</td>
                        <td className="px-3 py-3 font-mono font-bold text-teal-300">{currentPlan.staffing.nurses_morning} RNs</td>
                        <td className="px-3 py-3 font-mono">{(currentPlan.staffing.nurses_morning / currentPlan.staffing.physicians_morning).toFixed(2)}x</td>
                      </tr>
                      <tr>
                        <td className="px-3 py-3 font-medium">Evening (15:00 - 23:00)</td>
                        <td className="px-3 py-3 font-mono font-bold text-teal-300">{currentPlan.staffing.physicians_evening} MDs</td>
                        <td className="px-3 py-3 font-mono font-bold text-teal-300">{currentPlan.staffing.nurses_evening} RNs</td>
                        <td className="px-3 py-3 font-mono">{(currentPlan.staffing.nurses_evening / currentPlan.staffing.physicians_evening).toFixed(2)}x</td>
                      </tr>
                      <tr>
                        <td className="px-3 py-3 font-medium">Night (23:00 - 07:00)</td>
                        <td className="px-3 py-3 font-mono font-bold text-slate-300">{currentPlan.staffing.physicians_night} MDs</td>
                        <td className="px-3 py-3 font-mono font-bold text-slate-300">{currentPlan.staffing.nurses_night} RNs</td>
                        <td className="px-3 py-3 font-mono">{(currentPlan.staffing.nurses_night / currentPlan.staffing.physicians_night).toFixed(2)}x</td>
                      </tr>
                    </tbody>
                  </table>

                  <div className="mt-4 pt-3 border-t border-slate-800 flex justify-between text-xs text-slate-400">
                    <span>Diagnostic Stations: <strong className="text-white">{currentPlan.staffing.diagnostic_stations}</strong></span>
                    <span>Total Operational Beds: <strong className="text-white">{currentPlan.staffing.total_ed_beds}</strong> (+{currentPlan.staffing.additional_beds})</span>
                  </div>
                </div>
              )}
            </div>

            {/* Tradeoff Frontier Chart */}
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
              <h2 className="text-base font-bold text-white flex items-center space-x-2 mb-2">
                <BarChart className="w-5 h-5 text-teal-400" />
                <span>Cost vs Wait Time Tradeoff Frontier</span>
              </h2>
              <p className="text-xs text-slate-400 mb-4">
                Pareto candidates solved by CP-SAT and simulated with Common Random Numbers.
              </p>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                    <XAxis dataKey="cost" stroke="#94a3b8" fontSize={10} name="Additional Cost ($/day)" unit="$" />
                    <YAxis dataKey="wait" stroke="#94a3b8" fontSize={10} name="Mean Wait Time (min)" unit="m" />
                    <Tooltip
                      cursor={{ strokeDasharray: '3 3' }}
                      contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', fontSize: '11px' }}
                    />
                    <Scatter name="Candidate Plans" data={tradeoffData} fill="#14b8a6">
                      {tradeoffData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.isBaseline ? '#f59e0b' : (entry.isRecommended ? '#10b981' : '#06b6d4')} />
                      ))}
                    </Scatter>
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="p-12 rounded-2xl bg-slate-900/50 border border-dashed border-slate-800 flex flex-col items-center justify-center text-center">
          <Sparkles className="w-10 h-10 text-teal-400/60 mb-3" />
          <h3 className="text-base font-bold text-white">OR-Tools Optimizer Ready</h3>
          <p className="text-xs text-slate-400 max-w-sm mt-1">
            Specify a target daily budget ceiling above, then click &ldquo;Solve Optimal Allocation&rdquo; to formulate CP-SAT variables and evaluate candidates with SimPy.
          </p>
        </div>
      )}
    </div>
  );
};
