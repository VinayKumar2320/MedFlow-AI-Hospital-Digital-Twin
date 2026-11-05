import React from 'react';
import { useStore, PageId } from '../store/useStore';
import {
  Activity,
  TrendingUp,
  Cpu,
  Sliders,
  Sparkles,
  Layers,
  Brain,
  ShieldCheck,
  Building2,
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { currentPage, setCurrentPage, selectedProfileId, setSelectedProfileId } = useStore();

  const navItems: Array<{ id: PageId; label: string; icon: React.FC<{ className?: string }> }> = [
    { id: 'command_center', label: 'Command Center', icon: Activity },
    { id: 'forecasting', label: 'Demand Forecasting', icon: TrendingUp },
    { id: 'digital_twin', label: 'Digital Twin Sim', icon: Cpu },
    { id: 'scenario_lab', label: 'What-If Lab', icon: Sliders },
    { id: 'optimization', label: 'Optimization Studio', icon: Sparkles },
    { id: 'comparison', label: 'Scenario Comparison', icon: Layers },
    { id: 'model_intelligence', label: 'Model Intelligence', icon: Brain },
  ];

  return (
    <header className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-md border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentPage('command_center')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-teal-500/20">
              <Activity className="w-6 h-6 text-slate-950 font-black" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight text-white">MedFlow</span>
                <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20">
                  DIGITAL TWIN
                </span>
              </div>
              <p className="text-xs text-slate-400">Emergency Operations Optimizer</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentPage(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-teal-500/15 text-teal-300 border border-teal-500/30 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-teal-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Right Status & Hospital Profile Switcher */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/60">
              <Building2 className="w-4 h-4 text-slate-400" />
              <select
                value={selectedProfileId}
                onChange={(e) => setSelectedProfileId(e.target.value)}
                className="bg-transparent text-xs font-medium text-slate-200 outline-none cursor-pointer"
              >
                <option value="community" className="bg-slate-900 text-slate-200">Valley Community (15 Beds)</option>
                <option value="urban" className="bg-slate-900 text-slate-200">Metro Urban Center (32 Beds)</option>
                <option value="metropolitan" className="bg-slate-900 text-slate-200">St. Jude Trauma (75 Beds)</option>
              </select>
            </div>

            <div className="hidden lg:flex items-center space-x-1.5 px-2.5 py-1 rounded-md bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>SimPy 4.1 + OR-Tools Active</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
