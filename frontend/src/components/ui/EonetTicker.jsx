import React, { useEffect } from 'react';
import { useArkStore } from '../../store/arkStore';
import { useShallow } from 'zustand/react/shallow';

// 1. Import the direct NASA polling service
import { useEONETPolling } from '../../services/eonetService';

const EonetTicker = () => {
  // 2. Bypass the global store and backend completely. 
  // This component now manages its own survival via direct NASA connection.
  const liveEvents = useEONETPolling();

  return (
    <div className="flex flex-col h-36 border-t border-ark-border bg-[#0B0F19]/60">
      
      {/* Ticker Header */}
      <div className="px-3 py-1.5 border-b border-ark-border/50 bg-[#0B0F19] flex items-center justify-between">
        <span className="font-mono text-[9px] text-cyan-500 font-bold tracking-widest flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse"></span>
          LIVE EONET TELEMETRY
        </span>
        <span className="font-mono text-[9px] text-ark-silver tracking-widest">
          SYNC: DIRECT_API
        </span>
      </div>

      {/* Scrolling Feed Container */}
      <div className="flex-1 relative overflow-hidden">
        
        {/* FIXED CSS gradients to fade out the top and bottom of the list */}
        <div className="absolute top-0 left-0 right-0 h-4 bg-gradient-to-b from-[#0B0F19] to-transparent z-10 pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 right-0 h-4 bg-gradient-to-t from-[#0B0F19] to-transparent z-10 pointer-events-none"></div>

        {/* The actual scrolling list with a custom high-tech scrollbar */}
        <div className="absolute inset-0 overflow-y-auto p-3 space-y-1.5 [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-cyan-900/40 hover:[&::-webkit-scrollbar-thumb]:bg-cyan-400/80 [&::-webkit-scrollbar-thumb]:rounded-full">
          
          {liveEvents.length === 0 ? (
            <div className="font-mono text-[10px] text-ark-silver/50 animate-pulse mt-2">Awaiting satellite handshake...</div>
          ) : (
            liveEvents.map((item) => (
              <div key={item.id} className="flex items-center gap-3 font-mono text-[10px] animate-in slide-in-from-top-2 fade-in duration-300">
                {/* Note: Changed item.time to item.date to match your eonetService output */}
                <span className="text-ark-silver/40 min-w-[55px]">{item.date}</span>
                
                {/* Ensure coordinates exist before calling toFixed to prevent crashes */}
                <span className="text-cyan-400/80 min-w-[85px]">
                  [{item.lat?.toFixed(1) || "0.0"}, {item.lon?.toFixed(1) || "0.0"}]
                </span>
                
                <span className="text-slate-300 truncate">{item.title}</span>
              </div>
            ))
          )}
          
        </div>
      </div>
    </div>
  );
};

export default EonetTicker;