import React from 'react';
import { useStore } from '../store/useStore';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { Layers, CheckCircle2, TrendingDown, ArrowRight, ShieldCheck } from 'lucide-react';

export const ScenarioComparison: React.FC = () => {
  const { activeOptimization } = useStore();

  // Synthetic scenario comparison data (Baseline vs +40% Surge vs Optimized Staffing)
  const comparisonData = [
    {
      metric: 'Mean Wait (min)',
      Baseline: 38.5,
      Surge_40: 84.2,
      Optimized: 46.1,
    },
    {
      metric: 'P95 Wait (min)',
      Baseline: 68.0,
      Surge_40: 162.5,
      Optimized: 82.0,
    },
    {
      metric: 'Length of Stay (min)',
      Baseline: 142.0,
      Surge_40: 228.4,
      Optimized: 165.2,
    },
    {
      metric: 'Hourly Throughput',
      Baseline: 11.8,
      Surge_40: 14.1,
      Optimized: 16.9,
    },
  ];

  const utilizationData = [
    { resource: 'Nurses', Baseline: 64.2, Surge_40: 93.8, Optimized: 76.5 },
    { resource: 'Physicians', Baseline: 58.0, Surge_40: 88.4, Optimized: 72.1 },
    { resource: 'ED Beds', Baseline: 72.5, Surge_40: 96.2, Optimized: 81.0 },
    { resource: 'Diagnostics', Baseline: 51.4, Surge_40: 89.1, Optimized: 69.4 },
  ];

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <div className="flex items-center space-x-2">
          <h1 className="text-2xl font-bold tracking-tight text-white">Controlled Scenario Comparison</h1>
          <span className="px-2 py-0.5 rounded text-xs font-semibold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
            Paired Common Random Numbers
          </span>
        </div>
        <p className="text-sm text-slate-400 mt-1">
          Evaluating operational resilience: comparing Nominal Baseline vs 40% Surge Disruption vs OR-Tools Optimized Response.
        </p>
      </div>

      {/* Scenario Columns High-Level Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Scenario 1 */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Scenario 1: Baseline</span>
          <h3 className="text-lg font-bold text-white mt-1">Nominal Operations</h3>
          <p className="text-xs text-slate-400 mt-1">Standard diurnal arrival curve with baseline staffing (8 MDs, 16 RNs, 32 Beds).</p>
          <div className="mt-4 pt-3 border-t border-slate-800 space-y-1.5 text-xs">
            <div className="flex justify-between"><span className="text-slate-400">Mean Wait:</span> <strong className="text-white">38.5 min</strong></div>
            <div className="flex justify-between"><span className="text-slate-400">P95 Wait:</span> <strong className="text-white">68.0 min</strong></div>
            <div className="flex justify-between"><span className="text-slate-400">Daily Cost:</span> <strong className="text-white">$31,440</strong></div>
          </div>
        </div>

        {/* Scenario 2 */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-rose-500/30 relative overflow-hidden">
          <div className="absolute top-0 right-0 px-3 py-1 bg-rose-500/20 text-rose-300 text-[10px] font-bold uppercase tracking-wider rounded-bl-xl border-l border-b border-rose-500/30">
            Crisis Surge
          </div>
          <span className="text-xs font-bold uppercase tracking-wider text-rose-400">Scenario 2: Unmitigated Surge</span>
          <h3 className="text-lg font-bold text-white mt-1">+40% Patient Surge</h3>
          <p className="text-xs text-slate-400 mt-1">Severe arrival spike without operational staffing adjustments.</p>
          <div className="mt-4 pt-3 border-t border-slate-800 space-y-1.5 text-xs">
            <div className="flex justify-between"><span className="text-slate-400">Mean Wait:</span> <strong className="text-rose-400">84.2 min (+118%)</strong></div>
            <div className="flex justify-between"><span className="text-slate-400">P95 Wait:</span> <strong className="text-rose-400">162.5 min</strong></div>
            <div className="flex justify-between"><span className="text-slate-400">Daily Cost:</span> <strong className="text-white">$31,440</strong></div>
          </div>
        </div>

        {/* Scenario 3 */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-teal-500/40 relative overflow-hidden">
          <div className="absolute top-0 right-0 px-3 py-1 bg-teal-500/20 text-teal-300 text-[10px] font-bold uppercase tracking-wider rounded-bl-xl border-l border-b border-teal-500/30">
            Recommended
          </div>
          <span className="text-xs font-bold uppercase tracking-wider text-teal-400">Scenario 3: Mitigated</span>
          <h3 className="text-lg font-bold text-white mt-1">+40% Surge + Optimized Staff</h3>
          <p className="text-xs text-slate-400 mt-1">CP-SAT shift reallocation (+3 MDs peak, +6 RNs peak, +1 CT).</p>
          <div className="mt-4 pt-3 border-t border-slate-800 space-y-1.5 text-xs">
            <div className="flex justify-between"><span className="text-slate-400">Mean Wait:</span> <strong className="text-teal-300">46.1 min (-45.2% vs surge)</strong></div>
            <div className="flex justify-between"><span className="text-slate-400">P95 Wait:</span> <strong className="text-teal-300">82.0 min</strong></div>
            <div className="flex justify-between"><span className="text-slate-400">Daily Cost:</span> <strong className="text-white">$36,880 (+$5,440)</strong></div>
          </div>
        </div>
      </div>

      {/* Grouped Comparative Bar Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <h3 className="text-sm font-bold text-white mb-2 flex items-center space-x-2">
            <Layers className="w-4 h-4 text-teal-400" />
            <span>Patient Flow Delays &amp; Length of Stay</span>
          </h3>
          <p className="text-xs text-slate-400 mb-4">Values in minutes across common random number replications.</p>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData} margin={{ top: 10, right: 20, bottom: 20, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="metric" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', fontSize: '11px' }} />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Bar dataKey="Baseline" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Surge_40" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Optimized" fill="#14b8a6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <h3 className="text-sm font-bold text-white mb-2 flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span>Resource Utilization Stress (%)</span>
          </h3>
          <p className="text-xs text-slate-400 mb-4">Shows prevention of acute staff burnout and queue congestion.</p>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={utilizationData} margin={{ top: 10, right: 20, bottom: 20, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="resource" stroke="#94a3b8" fontSize={11} />
                <YAxis stroke="#94a3b8" fontSize={11} unit="%" />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', fontSize: '11px' }} />
                <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                <Bar dataKey="Baseline" fill="#94a3b8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Surge_40" fill="#f43f5e" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Optimized" fill="#06b6d4" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
