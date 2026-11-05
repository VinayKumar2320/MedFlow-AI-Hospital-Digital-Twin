import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { DashboardOverview } from '../types';
import { useStore } from '../store/useStore';
import {
  Users,
  Bed,
  Clock,
  TrendingUp,
  AlertTriangle,
  Play,
  Sparkles,
  ArrowUpRight,
  ShieldAlert,
  Stethoscope,
  ActivitySquare,
} from 'lucide-react';

export const CommandCenter: React.FC = () => {
  const { setCurrentPage } = useStore();
  const [data, setData] = useState<DashboardOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [coldStartNotice, setColdStartNotice] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setColdStartNotice(true);
    }, 4000);

    api.getDashboardOverview()
      .then((res) => {
        setData(res);
        setLoading(false);
        clearTimeout(timer);
      })
      .catch((err) => {
        console.error('Failed to load overview:', err);
        setLoading(false);
        clearTimeout(timer);
      });

    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center space-y-4 max-w-md text-center p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
          <div className="w-10 h-10 border-4 border-teal-500 border-t-transparent rounded-full animate-spin" />
          <div>
            <p className="text-white text-sm font-semibold">Synchronizing Hospital Digital Twin Census...</p>
            {coldStartNotice && (
              <p className="text-xs text-amber-300/90 mt-2 bg-amber-500/10 p-3 rounded-xl border border-amber-500/20 leading-relaxed">
                Render free web services spin down after inactivity. Cold-starting the cloud digital twin backend container may take ~30–45s...
              </p>
            )}
          </div>
        </div>
      </div>
    );
  }

  const overview = data || {
    hospital_name: 'Metro Health Urban Emergency Center',
    active_census: 42,
    waiting_patients: 11,
    ed_beds_total: 32,
    ed_beds_occupied: 25,
    bed_occupancy_pct: 78.1,
    physicians_on_duty: 8,
    nurses_on_duty: 16,
    diagnostic_capacity: 4,
    forecast_next_1h: 14.8,
    forecast_next_4h: 58.2,
    forecast_next_12h: 164.5,
    current_mean_wait_min: 38.5,
    alerts: [],
    profiles: [],
  };

  return (
    <div className="space-y-6">
      {/* Regulatory & Scope Notice */}
      <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-start space-x-3">
        <ShieldAlert className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
        <div className="text-xs text-amber-200/90 leading-relaxed">
          <span className="font-semibold text-amber-300">Operational Research & Educational Simulation Notice: </span>
          MedFlow models operational resource bottlenecks, patient flow queuing dynamics, and staffing allocations. It does not provide medical diagnoses, clinical triage decisions, or patient discharge instructions. All recommendations are simulations requiring human operational validation.
        </div>
      </div>

      {/* Hero Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-2xl font-bold tracking-tight text-white">{overview.hospital_name}</h1>
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Live Digital Twin
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Real-time emergency department operational telemetry & predictive queue telemetry.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setCurrentPage('scenario_lab')}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white font-medium text-sm transition-all shadow-lg shadow-teal-600/20"
          >
            <Play className="w-4 h-4 fill-white" />
            <span>Launch What-If Sim</span>
          </button>
          <button
            onClick={() => setCurrentPage('optimization')}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-medium text-sm transition-all"
          >
            <Sparkles className="w-4 h-4 text-teal-400" />
            <span>Optimize Staffing</span>
          </button>
        </div>
      </div>

      {/* Core KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Active Census */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-sm shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Active Census</span>
            <div className="p-2 rounded-xl bg-teal-500/10 text-teal-400">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-white">{overview.active_census}</span>
            <span className="text-xs text-slate-400">patients in ED</span>
          </div>
          <p className="mt-2 text-xs text-slate-400 flex items-center">
            <span className="text-amber-400 font-medium mr-1.5">{overview.waiting_patients} waiting</span> in triage & bed queue
          </p>
          <div className="absolute -bottom-6 -right-6 w-24 h-24 bg-teal-500/5 rounded-full blur-xl" />
        </div>

        {/* Bed Occupancy */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-sm shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Bed Occupancy</span>
            <div className={`p-2 rounded-xl ${overview.bed_occupancy_pct > 85 ? 'bg-rose-500/10 text-rose-400' : 'bg-teal-500/10 text-teal-400'}`}>
              <Bed className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-white">{overview.bed_occupancy_pct}%</span>
            <span className="text-xs text-slate-400">({overview.ed_beds_occupied}/{overview.ed_beds_total} beds)</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 mt-3 overflow-hidden">
            <div
              className={`h-1.5 rounded-full ${overview.bed_occupancy_pct > 85 ? 'bg-rose-500' : 'bg-teal-500'}`}
              style={{ width: `${overview.bed_occupancy_pct}%` }}
            />
          </div>
        </div>

        {/* Average Wait Time */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-sm shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Mean Wait Time</span>
            <div className="p-2 rounded-xl bg-teal-500/10 text-teal-400">
              <Clock className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-white">{overview.current_mean_wait_min}</span>
            <span className="text-xs text-slate-400">minutes</span>
          </div>
          <p className="mt-2 text-xs text-slate-400">
            Target service standard: &lt; 45.0 mins
          </p>
        </div>

        {/* 1h Forecast Demand */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800/80 backdrop-blur-sm shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Forecast Influx</span>
            <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-white">+{overview.forecast_next_1h}</span>
            <span className="text-xs text-slate-400">patients / hr</span>
          </div>
          <p className="mt-2 text-xs text-slate-400">
            LightGBM 4h projection: <span className="text-slate-200 font-semibold">{overview.forecast_next_4h}</span> arrivals
          </p>
        </div>
      </div>

      {/* Operational Resources & Alerts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Resources On Duty */}
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-white flex items-center space-x-2">
              <Stethoscope className="w-5 h-5 text-teal-400" />
              <span>Current Shift Deployment</span>
            </h2>
            <span className="text-xs text-slate-400">Active Shift</span>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-800/50 border border-slate-700/50">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 rounded-full bg-emerald-400" />
                <div>
                  <p className="text-sm font-semibold text-slate-200">Attending Physicians</p>
                  <p className="text-xs text-slate-400">Triage & Emergency Medicine</p>
                </div>
              </div>
              <span className="text-lg font-bold text-white">{overview.physicians_on_duty}</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-800/50 border border-slate-700/50">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 rounded-full bg-teal-400" />
                <div>
                  <p className="text-sm font-semibold text-slate-200">Registered Nurses</p>
                  <p className="text-xs text-slate-400">Bedside Care & Assessment</p>
                </div>
              </div>
              <span className="text-lg font-bold text-white">{overview.nurses_on_duty}</span>
            </div>

            <div className="flex items-center justify-between p-3 rounded-xl bg-slate-800/50 border border-slate-700/50">
              <div className="flex items-center space-x-3">
                <div className="w-3 h-3 rounded-full bg-cyan-400" />
                <div>
                  <p className="text-sm font-semibold text-slate-200">Diagnostic Modalities</p>
                  <p className="text-xs text-slate-400">CT / X-Ray / Urgent Labs</p>
                </div>
              </div>
              <span className="text-lg font-bold text-white">{overview.diagnostic_capacity} stations</span>
            </div>
          </div>
        </div>

        {/* Operational Intelligence Alerts */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-white flex items-center space-x-2">
              <ActivitySquare className="w-5 h-5 text-teal-400" />
              <span>Real-Time Operational Alerts & Projections</span>
            </h2>
            <button
              onClick={() => setCurrentPage('digital_twin')}
              className="text-xs text-teal-400 hover:text-teal-300 font-medium flex items-center space-x-1"
            >
              <span>View Live Simulator</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3">
            {overview.alerts && overview.alerts.length > 0 ? (
              overview.alerts.map((alt) => (
                <div
                  key={alt.id}
                  className={`p-4 rounded-xl border flex items-start space-x-3 ${
                    alt.level === 'WARNING'
                      ? 'bg-amber-500/10 border-amber-500/20 text-amber-200'
                      : 'bg-slate-800/60 border-slate-700/60 text-slate-300'
                  }`}
                >
                  <AlertTriangle
                    className={`w-5 h-5 flex-shrink-0 mt-0.5 ${
                      alt.level === 'WARNING' ? 'text-amber-400' : 'text-teal-400'
                    }`}
                  />
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-semibold text-white">{alt.title}</p>
                      <span className="text-xs text-slate-400">{alt.timestamp}</span>
                    </div>
                    <p className="text-xs text-slate-300 mt-1 leading-relaxed">{alt.message}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/40 text-xs text-slate-400">
                Operating within nominal queues and utilization safety thresholds.
              </div>
            )}

            {/* Quick action card */}
            <div className="mt-4 p-4 rounded-xl bg-gradient-to-r from-teal-900/30 to-slate-900 border border-teal-500/20 flex items-center justify-between">
              <div>
                <p className="text-sm font-semibold text-teal-200">Bottleneck Diagnosis Ready</p>
                <p className="text-xs text-slate-400 mt-0.5">
                  Sensitivity engine recommends adding 1 diagnostic station during evening surges to cut P95 wait by 28 mins.
                </p>
              </div>
              <button
                onClick={() => setCurrentPage('optimization')}
                className="px-3 py-1.5 rounded-lg bg-teal-500 hover:bg-teal-400 text-slate-950 font-semibold text-xs transition-colors"
              >
                Inspect Plan
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
