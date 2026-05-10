import React, { useEffect, useState, memo } from 'react';
import { useArkStore } from '../../store/arkStore';
import { useShallow } from 'zustand/react/shallow';

const MetricsBar = () => {
  // 1. Strict Subscription: Only re-render if these specific values change
  const { 
    totalPesoLoss, 
    totalComputeSavedUsd, 
    latencyMs, 
    pipelineStatus 
  } = useArkStore(
    useShallow((state) => ({
      totalPesoLoss: state.totalPesoLoss,
      totalComputeSavedUsd: state.totalComputeSavedUsd,
      latencyMs: state.latencyMs,
      pipelineStatus: state.pipelineStatus,
    }))
  );

  // 2. Flash Animation State for Peso Loss
  const [isFlashing, setIsFlashing] = useState(false);

  useEffect(() => {
    if (totalPesoLoss > 0) {
      setIsFlashing(true);
      const timer = setTimeout(() => setIsFlashing(false), 300);
      return () => clearTimeout(timer);
    }
  }, [totalPesoLoss]);

  // 3. Latency Dot Logic
  const getLatencyColor = () => {
    if (latencyMs < 100) return 'text-green-500';
    if (latencyMs < 500) return 'text-amber-500';
    return 'text-rose-500';
  };

  return (
    <div className="w-full flex flex-col font-mono z-50">
      {/* MAIN TOP BAR */}
      <div className="flex items-center justify-between px-6 py-2 bg-[#0B0F19]/90 border-b border-[#1E2A3A] backdrop-blur-sm">
        {/* Top Left Branding */}
        <div className="flex items-center space-x-4">
          <div className="font-mono text-cyan-400 font-bold tracking-widest text-lg">
            PROJECT ARK
          </div>
          <div className="hidden md:block w-px h-6 bg-ark-border"></div>
          <div className="hidden md:block font-mono text-ark-silver text-xs tracking-widest">
            DEVELOPED BY: MATLIH
          </div>
        </div>

        {/* RIGHT: Metric Cluster */}
        <div className="flex items-center space-x-6 text-sm">
          
          {/* Badge 1: Peso Loss */}
          <div className="flex flex-col items-end">
            <span className="text-[10px] text-ark-silver tracking-wider">PESO LOSS</span>
            <span className={`font-bold transition-colors duration-150 ${isFlashing ? 'text-rose-400' : 'text-amber-400'}`}>
              ₱ {(totalPesoLoss / 1e9).toFixed(2)}B
            </span>
          </div>

          <div className="h-6 w-px bg-ark-border" />

          {/* Badge 2: Compute Savings */}
          <div className="flex flex-col items-end">
            <span className="text-[10px] text-ark-silver tracking-wider">COMPUTE SAVINGS</span>
            <span className="font-bold text-cyan-400">
              $ {totalComputeSavedUsd.toFixed(2)}
            </span>
          </div>

          <div className="h-6 w-px bg-ark-border" />

          {/* Badge 3: Latency */}
          <div className="flex flex-col items-end">
            <span className="text-[10px] text-ark-silver tracking-wider">LATENCY</span>
            <div className="flex items-center space-x-1.5">
              <span className={`text-[10px] ${getLatencyColor()}`}>●</span>
              <span className="font-bold text-slate-300">
                {latencyMs}ms
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* STATUS SUB-BAR */}
      {pipelineStatus !== 'IDLE' && (
        <div className="w-full px-6 py-1 bg-ark-panel/80 border-b border-ark-border/50 text-xs">
          {pipelineStatus === 'RUNNING' && (
            <div className="flex items-center space-x-3 text-cyan-400">
              <span className="animate-pulse">●</span>
              <span className="animate-pulse tracking-wide uppercase">Analysis in progress...</span>
            </div>
          )}
          {pipelineStatus === 'COMPLETE' && (
            <div className="flex items-center space-x-3 text-green-400">
              <span>●</span>
              <span className="tracking-wide">Analysis Complete: Philippines Bounding Box Finalized.</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default memo(MetricsBar);