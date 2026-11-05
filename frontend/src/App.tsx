import React from 'react';
import { useStore } from './store/useStore';
import { Navbar } from './components/Navbar';
import { CommandCenter } from './pages/CommandCenter';
import { DemandForecasting } from './pages/DemandForecasting';
import { DigitalTwinSimulator } from './pages/DigitalTwinSimulator';
import { ScenarioLab } from './pages/ScenarioLab';
import { OptimizationStudio } from './pages/OptimizationStudio';
import { ScenarioComparison } from './pages/ScenarioComparison';
import { ModelIntelligence } from './pages/ModelIntelligence';
import { Activity, ShieldAlert, HeartPulse } from 'lucide-react';

export const App: React.FC = () => {
  const { currentPage } = useStore();

  const renderActivePage = () => {
    switch (currentPage) {
      case 'command_center':
        return <CommandCenter />;
      case 'forecasting':
        return <DemandForecasting />;
      case 'digital_twin':
        return <DigitalTwinSimulator />;
      case 'scenario_lab':
        return <ScenarioLab />;
      case 'optimization':
        return <OptimizationStudio />;
      case 'comparison':
        return <ScenarioComparison />;
      case 'model_intelligence':
        return <ModelIntelligence />;
      default:
        return <CommandCenter />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {renderActivePage()}
      </main>

      <footer className="bg-slate-900/60 border-t border-slate-800/80 mt-12 py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-400">
          <div className="flex items-center space-x-2">
            <HeartPulse className="w-4 h-4 text-teal-400" />
            <span className="font-semibold text-slate-200">MedFlow Operations Intelligence</span>
            <span>&bull; SimPy Discrete-Event Digital Twin &amp; Google OR-Tools CP-SAT</span>
          </div>

          <div className="text-center md:text-right text-[11px] text-slate-500 max-w-md">
            Operational research, capacity planning, and educational simulation platform. Does not make clinical medical decisions.
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
