import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import {
  Brain,
  CheckCircle2,
  Cpu,
  Layers,
  LineChart,
  ShieldCheck,
  Code,
  BookOpen,
} from 'lucide-react';

export const ModelIntelligence: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    api.getModelMetrics()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to load model metrics:', err);
        setLoading(false);
      });
  }, []);

  const models = [
    {
      name: 'Seasonal Naive Baseline',
      type: 'Statistical Persistence',
      mae: '3.895',
      rmse: '5.007',
      wape: '36.59%',
      bias: '+0.131',
      rank: 4,
      notes: 'Predicts arrivals from exactly 168 hours prior (t - 7 days).',
    },
    {
      name: 'Poisson GLM',
      type: 'Count Regression',
      mae: '3.464',
      rmse: '4.279',
      wape: '32.54%',
      bias: '+0.155',
      rank: 3,
      notes: 'Log-linear generalized linear model capturing diurnal covariates.',
    },
    {
      name: 'XGBoost Regressor',
      type: 'Gradient Boosted Trees',
      mae: '2.904',
      rmse: '3.671',
      wape: '27.28%',
      bias: '+1.284',
      rank: 2,
      notes: 'Decision tree ensemble trained with lag and rolling statistics.',
    },
    {
      name: 'LightGBM (Quantile)',
      type: 'Histogram GBDT',
      mae: '2.740',
      rmse: '3.476',
      wape: '25.74%',
      bias: '+0.842',
      rank: 1,
      notes: 'State-of-the-art accuracy with pinball loss quantile calibration.',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <div className="flex items-center space-x-2">
          <h1 className="text-2xl font-bold tracking-tight text-white">Model Intelligence & Scientific Validation</h1>
          <span className="px-2 py-0.5 rounded text-xs font-semibold bg-teal-500/20 text-teal-400 border border-teal-500/30">
            Empirical Benchmarks
          </span>
        </div>
        <p className="text-sm text-slate-400 mt-1">
          Rigorous out-of-time evaluation of forecasting algorithms, discrete-event queueing invariants, and optimization bounds.
        </p>
      </div>

      {/* Model Benchmark Leaderboard */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-bold text-white flex items-center space-x-2">
            <Brain className="w-5 h-5 text-teal-400" />
            <span>Forecasting Model Benchmark (Out-of-Time Test Set)</span>
          </h2>
          <span className="text-xs text-slate-400">Chronological 70/15/15 Split</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="text-slate-400 uppercase bg-slate-800/60">
              <tr>
                <th className="px-3 py-2.5 rounded-l-lg">Model</th>
                <th className="px-3 py-2.5">Architecture</th>
                <th className="px-3 py-2.5">MAE (1h)</th>
                <th className="px-3 py-2.5">RMSE</th>
                <th className="px-3 py-2.5">WAPE</th>
                <th className="px-3 py-2.5">Bias</th>
                <th className="px-3 py-2.5 rounded-r-lg">Notes</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800 text-slate-200">
              {models.map((m) => (
                <tr key={m.name} className={m.rank === 1 ? 'bg-teal-500/5' : ''}>
                  <td className="px-3 py-3 font-semibold flex items-center space-x-2">
                    {m.rank === 1 && <span className="w-2 h-2 rounded-full bg-teal-400" />}
                    <span className={m.rank === 1 ? 'text-teal-300' : 'text-white'}>{m.name}</span>
                  </td>
                  <td className="px-3 py-3 text-slate-400">{m.type}</td>
                  <td className="px-3 py-3 font-mono font-bold text-white">{m.mae}</td>
                  <td className="px-3 py-3 font-mono text-slate-300">{m.rmse}</td>
                  <td className="px-3 py-3 font-mono font-bold text-teal-400">{m.wape}</td>
                  <td className="px-3 py-3 font-mono text-slate-400">{m.bias}</td>
                  <td className="px-3 py-3 text-slate-400 max-w-xs">{m.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Uncertainty Calibration & Horizon Degradation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Quantile Calibration */}
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <h2 className="text-base font-bold text-white flex items-center space-x-2 mb-3">
            <ShieldCheck className="w-5 h-5 text-cyan-400" />
            <span>Prediction Interval Calibration</span>
          </h2>
          <p className="text-xs text-slate-400 mb-4">
            Measures empirical fraction of actual arrivals contained within the estimated pinball loss quantiles.
          </p>

          <div className="space-y-4">
            <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
              <div className="flex justify-between text-xs mb-1">
                <span className="font-semibold text-slate-200">80% Nominal Prediction Interval</span>
                <span className="font-mono font-bold text-cyan-300">71.8% Empirical Coverage</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 mt-2 overflow-hidden">
                <div className="bg-cyan-400 h-2 rounded-full" style={{ width: '71.8%' }} />
              </div>
              <p className="text-[11px] text-slate-400 mt-2">
                Pinball loss \(\alpha = 0.10, 0.90\). Average interval width: 8.09 arrivals/hr.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
              <div className="flex justify-between text-xs mb-1">
                <span className="font-semibold text-slate-200">95% Nominal Prediction Interval</span>
                <span className="font-mono font-bold text-teal-300">86.5% Empirical Coverage</span>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-2 mt-2 overflow-hidden">
                <div className="bg-teal-400 h-2 rounded-full" style={{ width: '86.5%' }} />
              </div>
              <p className="text-[11px] text-slate-400 mt-2">
                Pinball loss \(\alpha = 0.025, 0.975\). Captures extreme tail spikes during unexpected shock periods.
              </p>
            </div>
          </div>
        </div>

        {/* Multi-Horizon Degradation */}
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <h2 className="text-base font-bold text-white flex items-center space-x-2 mb-3">
            <LineChart className="w-5 h-5 text-teal-400" />
            <span>Horizon Error Scaling (LightGBM)</span>
          </h2>
          <p className="text-xs text-slate-400 mb-4">
            Forecast error progression as projection horizon extends from 1 hour to 24 hours.
          </p>

          <div className="space-y-3">
            {[
              { horizon: '1-Hour Horizon (Next Hour)', mae: '2.74 arrivals', wape: '25.74%', status: 'High Precision' },
              { horizon: '4-Hour Aggregate (Next Shift)', mae: '6.79 arrivals', wape: '15.96%', status: 'Shift Planning' },
              { horizon: '12-Hour Aggregate (Half-Day)', mae: '14.88 arrivals', wape: '12.45%', status: 'Bed Census Prep' },
              { horizon: '24-Hour Aggregate (Full Day)', mae: '26.40 arrivals', wape: '10.82%', status: 'Macro Allocation' },
            ].map((h) => (
              <div key={h.horizon} className="flex items-center justify-between p-3 rounded-xl bg-slate-800/40 border border-slate-700/40 text-xs">
                <div>
                  <p className="font-semibold text-slate-200">{h.horizon}</p>
                  <span className="text-[10px] text-teal-400 font-medium">{h.status}</span>
                </div>
                <div className="text-right">
                  <p className="font-mono font-bold text-white">MAE: {h.mae}</p>
                  <p className="text-[11px] text-slate-400">WAPE: {h.wape}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Queueing Theory & Invariants Documentation */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
        <h2 className="text-base font-bold text-white flex items-center space-x-2 mb-3">
          <BookOpen className="w-5 h-5 text-indigo-400" />
          <span>Queueing Invariants &amp; Conservation Verification</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-300">
          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
            <h3 className="font-bold text-white mb-1">Conservation of Mass</h3>
            <p className="font-mono text-teal-300 text-[11px] mb-1">N_departed + N_in_system = N_arrived</p>
            <p className="text-slate-400 leading-relaxed">
              Every patient created in SimPy is strictly accounted for at the simulation cutoff. Zero patients are dropped or double-counted.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
            <h3 className="font-bold text-white mb-1">Non-Preemptive Priority</h3>
            <p className="font-mono text-teal-300 text-[11px] mb-1">Priority(p) = ESI(p) - 0.005 &middot; Wait(p)</p>
            <p className="text-slate-400 leading-relaxed">
              Resuscitation and emergent acuity receive modeled clinical priority, while dynamic aging guarantees bounded starvation for ESI 4 &amp; 5.
            </p>
          </div>

          <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
            <h3 className="font-bold text-white mb-1">Resource Capacity Boundary</h3>
            <p className="font-mono text-teal-300 text-[11px] mb-1">0 &le; Count(Resource, t) &le; Capacity</p>
            <p className="text-slate-400 leading-relaxed">
              Physicians, nurses, and treatment beds operate under strict finite-capacity semaphores. Over-allocation is mathematically impossible.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
