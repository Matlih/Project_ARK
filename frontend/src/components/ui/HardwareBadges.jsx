import React, { memo } from 'react';

// Static branding elements. Fully decoupled from state.
const HardwareBadges = () => {
  return (
    <div className="absolute bottom-6 left-6 flex items-center space-x-3 z-40 pointer-events-auto select-none">
      
      {/* Badge 1: Hardware Specs */}
      <div className="flex items-center space-x-2 border border-slate-700/80 rounded-full px-3 py-1 bg-ark-panel/60 backdrop-blur-sm shadow-[0_0_8px_rgba(34,211,238,0.15)] hover:border-cyan-400/40 transition-colors border-l-rose-600 border-l-2">
        <div className="w-2 h-2 bg-rose-600 rounded-sm" />
        <div className="flex flex-col">
          <span className="text-[10px] font-mono text-slate-300 leading-none pb-0.5">
            AMD Instinct™ MI300X
          </span>
          <span className="text-[8px] font-mono text-ark-silver leading-none">
            192 GB HBM3 VRAM
          </span>
        </div>
      </div>

      {/* Badge 2: Software Stack */}
      <div className="flex items-center border border-slate-700/80 rounded-full px-3 py-1.5 bg-ark-panel/60 backdrop-blur-sm shadow-[0_0_8px_rgba(34,211,238,0.15)] hover:border-cyan-400/40 transition-colors">
        <span className="text-[10px] font-mono text-slate-400">
          ROCm 6.x | <span className="text-cyan-400">3 Parallel Streams</span>
        </span>
      </div>

      {/* Badge 3: Project Version */}
      <div className="flex items-center border border-slate-700/80 rounded-full px-3 py-1.5 bg-ark-panel/60 backdrop-blur-sm shadow-[0_0_8px_rgba(34,211,238,0.15)] hover:border-cyan-400/40 transition-colors">
        <span className="text-[10px] font-mono text-ark-silver font-bold tracking-widest">
          PROJECT ARK V1.0
        </span>
      </div>

    </div>
  );
};

export default memo(HardwareBadges);