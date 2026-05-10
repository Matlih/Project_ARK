import React, { useEffect, useState } from 'react';
import { useArkStore } from './store/arkStore';
import { useShallow } from 'zustand/react/shallow';
import { useARKSocket, triggerPipeline, resetSystem } from './services/useARKSocket';

// Layout Components
import MetricsBar from './components/ui/MetricsBar';
import ARKGlobe from './components/globe/ARKGlobe';
import AnalysisProgress from './components/ui/AnalysisProgress';
import HardwareBadges from './components/ui/HardwareBadges';
import AgentLog from './components/ui/AgentLog';
import NDRRMCReport from './components/ui/NDRRMCReport';
import BootSequence from './components/ui/BootSequence';
import ReportArchive from './components/ui/ReportArchive';
import EonetTicker from './components/ui/EonetTicker';

// J.A.R.V.I.S. Text-to-Speech
import { JarvisVisualizer } from './components/ui/JarvisVisualizer';


const App = () => {
  // 1. Mount the core WebSocket connection (Singleton)
  useARKSocket();

  // 2. Local state for the region selector (Default to Sector 1)
  const [selectedRegion, setSelectedRegion] = useState('Philippines: Luzon');

  // 3. Strict state subscription for UI locking
  const pipelineStatus = useArkStore(useShallow((state) => state.pipelineStatus));
  
  // 4. Boot state
  const [isBooting, setIsBooting] = useState(true);

  // 5. Initialization Sequence Effect
  useEffect(() => {
    const store = useArkStore.getState();
    const initLogs = [
      { type: 'system', agent: 'SYSTEM', message: 'System initialized. Waiting for EONET' },
      { type: 'system', agent: 'SYSTEM', message: 'Ping: Node communication check at [385ms]' },
      { type: 'system', agent: 'ROCm', message: 'MI300X streams standby. 192GB HBM3 available.' }
    ];

    const timeouts = initLogs.map((log, index) => {
      return setTimeout(() => {
        store.addAgentLog({
          ...log,
          timestamp: new Date().toLocaleTimeString()
        });
      }, (index + 1) * 500); // 500ms, 1000ms, 1500ms
    });

    return () => timeouts.forEach(clearTimeout);
  }, []);
  
    // --- TACTICAL AUDIO HANDLERS ---
  const handleRunPipeline = () => {
    // 1. Play the mechanical click
    new Audio('/run_ark_pipeline.wav').play().catch(e => console.log("Audio blocked:", e));
    // 2. Trigger the WebSocket payload
    triggerPipeline(selectedRegion);
  };
  
  return (
    <>
      {/* Boot Sequence Overlay */}
      {isBooting && <BootSequence onComplete={() => setIsBooting(false)} />}

      {/* Main Application Layout (loads in background) */}
      <div className="h-screen w-screen bg-[#0B0F19] bg-[radial-gradient(circle,#1E2A3A_1px,transparent_1px)] bg-[size:24px_24px] overflow-hidden grid grid-rows-[auto_1fr_auto]">
        
        {/* Row 1: Top metrics bar */}
        <MetricsBar />
        
        {/* Row 2: Main content */}
        <div className="grid grid-cols-[1fr_380px] gap-0 overflow-hidden">
          
          {/* Left: Globe panel */}
          <div className="relative w-full h-full">
            <ARKGlobe />
            <AnalysisProgress />   {/* absolute bottom of this panel */}
            <HardwareBadges />     {/* absolute bottom-left */}
          </div>
          
          {/* Right: Intelligence panel */}
          <div className="flex flex-col border-l border-ark-border bg-ark-panel/50 backdrop-blur-sm relative">
            
            {/* The J.A.R.V.I.S. AI Core */}
            <div className="border-b border-ark-border flex justify-center bg-[#0B0F19]/40">
               <JarvisVisualizer />
            </div>

            {/* Notice how AgentLog is wrapped in flex-1 so it takes the remaining height */}
            <div className="flex-1 p-4 overflow-hidden relative">
              <AgentLog />
            </div>
            
            {/* NEW: The EONET Ticker sits securely at the bottom of the column */}
            <EonetTicker />
            
            {/* NDRRMCReport internally uses absolute positioning */}
            <div className="border-t border-ark-border">
              <NDRRMCReport />
            </div>
          </div>
          
        </div>
        
        {/* Row 3: Control bar */}
        <div className="flex flex-col">
          <div className="border-t border-ark-border bg-ark-panel px-4 py-3 flex items-center gap-4">
            <label className="text-ark-silver text-sm font-mono">Region</label>
            <select 
              className="bg-ark-bg border border-ark-border text-white font-mono text-sm rounded px-3 py-1.5 focus:border-cyan-400 focus:outline-none cursor-pointer"
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              disabled={pipelineStatus === 'RUNNING'}
            >
              <option value="Philippines: Luzon">Philippines: Luzon</option>
              <option value="Philippines: Visayas">Philippines: Visayas</option>
              <option value="Philippines: Mindanao">Philippines: Mindanao</option>
            </select>
            
            {/* NEW ARCHIVE BUTTON */}
            <button 
              onClick={() => useArkStore.getState().setArchiveOpen(true)}
              className="text-ark-silver hover:text-cyan-400 font-mono text-sm tracking-widest px-4 py-1.5 border border-transparent hover:border-cyan-400/50 rounded transition-colors"
            >
              [ REPORT ARCHIVE ]
            </button>

            <button
              onClick={handleRunPipeline}
              disabled={pipelineStatus === 'RUNNING'}
              className="ml-auto bg-slate-700 hover:bg-slate-600 disabled:opacity-40 disabled:cursor-not-allowed text-white font-mono text-sm tracking-widest px-8 py-2 rounded-full border border-slate-500 transition-all duration-200 hover:border-cyan-400/50 hover:shadow-[0_0_12px_rgba(34,211,238,0.2)]"
            >
              {pipelineStatus === 'RUNNING' ? 'PROCESSING...' : 'RUN ARK PIPELINE'}
            </button>
          </div>

          <button 
            onClick={resetSystem}
            className="w-full bg-slate-800/60 text-slate-500 font-mono text-xs tracking-widest py-1.5 hover:text-slate-300 transition-colors border-t border-ark-border"
          >
            RESET SYSTEM
          </button>
        </div>
      </div>
      
      {/* Mount the Archive Modal */}
      <ReportArchive />
    </>
  );
};

export default App;