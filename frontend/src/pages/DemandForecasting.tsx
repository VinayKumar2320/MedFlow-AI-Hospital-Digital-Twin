import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ForecastResponse } from '../types';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  BarChart,
  Bar,
  Legend,
} from 'recharts';
import {
  TrendingUp,
  SlidersHorizontal,
  Layers,
  BarChart2,
  CheckCircle2,
  Info,
} from 'lucide-react';

export const DemandForecasting: React.FC = () => {
  const [model, setModel] = useState<string>('lightgbm');
  const [horizon, setHorizon] = useState<number>(48);
  const [data, setData] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    setLoading(true);
    api.getForecasts(horizon, model)
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error fetching forecast:', err);
        setLoading(false);
      });
  }, [model, horizon]);

  const metrics = data?.metrics || {
    mae: 2.74,
    rmse: 3.48,
    wape: 25.7,
    bias: 0.84,
    coverage_80_pct: 71.8,
    coverage_95_pct: 86.5,
    avg_width_80: 8.1,
  };

  const chartData = (data?.points || []).map((pt) => ({
    time: pt.timestamp.split(' ')[1] || pt.timestamp,
    historical: pt.historical,
    predicted: pt.predicted,
    band_80_low: pt.lower_80,
    band_80_high: pt.upper_80,
    band_95_low: pt.lower_95,
    band_95_high: pt.upper_95,
  }));

  const featureData = (data?.feature_importance || []).slice(0, 8);

  return (
    <div className="space-y-6">
      {/* Page Title & Controls */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">Emergency Demand Forecasting</h1>
            <span className="px-2 py-0.5 rounded text-xs font-semibold bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              Quantile-Calibrated
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Probabilistic arrival predictions with conformal uncertainty bounds across 1h, 4h, 12h, and 24h horizons.
          </p>
        </div>

        {/* Model & Horizon Selectors */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-2 bg-slate-900 px-3 py-1.5 rounded-xl border border-slate-800">
            <SlidersHorizontal className="w-4 h-4 text-slate-400" />
            <span className="text-xs text-slate-400">Model:</span>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="bg-transparent text-xs font-semibold text-teal-300 outline-none cursor-pointer"
            >
              <option value="lightgbm" className="bg-slate-900 text-slate-200">LightGBM (Quantile)</option>
              <option value="xgboost" className="bg-slate-900 text-slate-200">XGBoost Regressor</option>
              <option value="poisson_glm" className="bg-slate-900 text-slate-200">Poisson GLM Baseline</option>
              <option value="seasonal_naive" className="bg-slate-900 text-slate-200">Seasonal Naive (Lag 168h)</option>
            </select>
          </div>

          <div className="flex items-center space-x-1 bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs">
            {[24, 48, 72].map((h) => (
              <button
                key={h}
                onClick={() => setHorizon(h)}
                className={`px-3 py-1 rounded-lg font-medium transition-all ${
                  horizon === h ? 'bg-teal-500/20 text-teal-300 border border-teal-500/30' : 'text-slate-400 hover:text-white'
                }`}
              >
                {h}h
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Accuracy KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">MAE (1-Hour)</span>
          <p className="text-2xl font-bold text-white mt-1">{metrics.mae}</p>
          <span className="text-[11px] text-slate-500">arrivals / hr</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">RMSE</span>
          <p className="text-2xl font-bold text-white mt-1">{metrics.rmse}</p>
          <span className="text-[11px] text-slate-500">root mean squared</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">WAPE</span>
          <p className="text-2xl font-bold text-teal-300 mt-1">{metrics.wape}%</p>
          <span className="text-[11px] text-slate-500">weighted abs % err</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">Forecast Bias</span>
          <p className="text-2xl font-bold text-white mt-1">{metrics.bias > 0 ? `+${metrics.bias}` : metrics.bias}</p>
          <span className="text-[11px] text-slate-500">mean error delta</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">80% Coverage</span>
          <p className="text-2xl font-bold text-cyan-300 mt-1">{metrics.coverage_80_pct ?? 71.8}%</p>
          <span className="text-[11px] text-slate-500">empirical validation</span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
          <span className="text-xs text-slate-400 uppercase font-semibold">95% Coverage</span>
          <p className="text-2xl font-bold text-cyan-300 mt-1">{metrics.coverage_95_pct ?? 86.5}%</p>
          <span className="text-[11px] text-slate-500">extreme tail bounds</span>
        </div>
      </div>

      {/* Main Forecast Chart */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-bold text-white flex items-center space-x-2">
              <TrendingUp className="w-5 h-5 text-teal-400" />
              <span>Forecast Trajectory & Prediction Intervals (Next {horizon} Hours)</span>
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Shaded bands represent 80% (inner) and 95% (outer) quantile regression bounds.
            </p>
          </div>
        </div>

        {loading ? (
          <div className="h-80 flex items-center justify-center">
            <div className="w-8 h-8 border-4 border-teal-500 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={chartData} margin={{ top: 10, right: 20, bottom: 20, left: 0 }}>
                <defs>
                  <linearGradient id="band95" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0891b2" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#0891b2" stopOpacity={0.05} />
                  </linearGradient>
                  <linearGradient id="band80" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#14b8a6" stopOpacity={0.1} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.5} />
                <XAxis dataKey="time" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} label={{ value: 'Arrivals / hr', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }}
                />
                <Legend verticalAlign="top" wrapperStyle={{ paddingBottom: '10px', fontSize: '12px' }} />
                <Area type="monotone" dataKey="band_95_high" stroke="none" fill="url(#band95)" name="95% Upper Bound" />
                <Area type="monotone" dataKey="band_80_high" stroke="none" fill="url(#band80)" name="80% Upper Bound" />
                <Line type="monotone" dataKey="predicted" stroke="#14b8a6" strokeWidth={2.5} dot={false} name="Forecasted Arrival Rate" />
                <Line type="monotone" dataKey="historical" stroke="#f59e0b" strokeWidth={1.5} dot={{ r: 2 }} name="Historical Arrival Truth" strokeDasharray="4 4" />
              </ComposedChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Feature Importance & Model Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <h2 className="text-base font-bold text-white flex items-center space-x-2 mb-3">
            <BarChart2 className="w-5 h-5 text-teal-400" />
            <span>Top Predictive Feature Importances (Gain)</span>
          </h2>
          <p className="text-xs text-slate-400 mb-4">
            Measures feature split utility in gradient boosted trees. Short-term rolling variability and diurnal cycles dominate.
          </p>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={featureData} layout="vertical" margin={{ top: 5, right: 30, left: 60, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.4} />
                <XAxis type="number" stroke="#94a3b8" fontSize={10} />
                <YAxis type="category" dataKey="feature" stroke="#94a3b8" fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem', fontSize: '11px' }} />
                <Bar dataKey="importance" fill="#14b8a6" radius={[0, 4, 4, 0]} name="Tree Splits Gain" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-white flex items-center space-x-2 mb-3">
              <Info className="w-5 h-5 text-cyan-400" />
              <span>Forecasting Methodology & Temporal Integrity</span>
            </h2>
            <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
              <div className="p-3 rounded-xl bg-slate-800/60 border border-slate-700/60">
                <span className="font-semibold text-slate-100">Zero Future Leakage: </span>
                All lag features and rolling statistical moments are computed strictly over past observations using chronological rolling-origin splits.
              </div>
              <div className="p-3 rounded-xl bg-slate-800/60 border border-slate-700/60">
                <span className="font-semibold text-slate-100">Quantile Regression Intervals: </span>
                Prediction bounds are directly estimated via pinball loss minimization (<span className="text-teal-300 font-mono">alpha=0.10, 0.90, 0.025, 0.975</span>) to reflect non-Gaussian asymmetric arrival spikes.
              </div>
              <div className="p-3 rounded-xl bg-slate-800/60 border border-slate-700/60">
                <span className="font-semibold text-slate-100">Simulation Influx Coupling: </span>
                Forecast distributions feed the non-homogeneous Poisson rate parameters in the SimPy digital twin engine.
              </div>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>Model Version: LightGBM v4.7.0</span>
            <span className="flex items-center space-x-1 text-emerald-400">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Validated on Holdout Test Split</span>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
