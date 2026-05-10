import React, { useMemo, memo } from 'react';
import { useArkStore } from '../../store/arkStore';
import { useShallow } from 'zustand/react/shallow';

const AnalysisProgress = () => {
  const { pipelineStatus, gateResults, agentLog } = useArkStore(
    useShallow((state) => ({
      pipelineStatus: state.pipelineStatus,
      gateResults: state.gateResults,
      agentLog: state.agentLog,
    }))
  );

  // Deterministic progress calculation based on pipeline milestones
  const progressPercent = useMemo(() => {
    let p = 0;
    
    // 1. Gate progression
    const gateCount = gateResults.length;
    if (gateCount === 1) p = Math.max(p, 15);
    if (gateCount === 2) p = Math.max(p, 25);
    if (gateCount >= 3) p = Math.max(p, 35);

    // 2. Agent progression
    // We scan the log array for specific agent names mentioning key phases
    const agentsSeen = new Set(agentLog.map(log => log.agent));

    // Loosely matching agent node names typical of the backend logic
    if (Array.from(agentsSeen).some(a => a.includes('damage_assessment'))) p = Math.max(p, 55);
    if (Array.from(agentsSeen).some(a => a.includes('economic_valuation'))) p = Math.max(p, 70);
    if (Array.from(agentsSeen).some(a => a.includes('insurance_trigger'))) p = Math.max(p, 80);
    if (Array.from(agentsSeen).some(a => a.includes('recovery_planner'))) p = Math.max(p, 90);
    if (Array.from(agentsSeen).some(a => a.includes('ndrrmc_reporter'))) p = Math.max(p, 100);

    // Force 100 if complete, regardless of log history
    if (pipelineStatus === 'COMPLETE') p = 100;

    return p;
  }, [gateResults.length, agentLog, pipelineStatus]);

  if (pipelineStatus !== 'RUNNING' && pipelineStatus !== 'COMPLETE') return null;

  return (
    <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-full max-w-2xl px-6 flex flex-col items-center z-40 pointer-events-none">
      <div className="font-mono text-xs text-ark-silver mb-2 tracking-widest bg-[#0B0F19]/50 px-3 py-1 rounded">
        ANALYSIS PROGRESS: <span className="text-cyan-400">{progressPercent}%</span>
      </div>
      
      {/* Progress Track */}
      <div className="w-full h-[2px] bg-slate-700 relative overflow-hidden rounded-full shadow-[0_0_10px_rgba(34,211,238,0.2)]">
        {/* Fill Line */}
        <div 
          className="h-full bg-cyan-400 transition-all duration-300 ease-out"
          style={{ width: `${progressPercent}%` }}
        />
      </div>
    </div>
  );
};

export default memo(AnalysisProgress);