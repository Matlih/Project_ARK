import React, { useEffect, useRef, useState, memo, useMemo } from 'react';
import { useArkStore } from '../../store/arkStore';
import { useShallow } from 'zustand/react/shallow';

// --- CUSTOM TYPEWRITER COMPONENT (IDEMPOTENT FIX) ---
const TypewriterText = memo(({ text, isLatest }) => {
  // If it's not the latest log, instantly show the full text length
  const [currentIndex, setCurrentIndex] = useState(isLatest ? 0 : text.length);

  useEffect(() => {
    if (!isLatest) {
      setCurrentIndex(text.length);
      return;
    }

    // Reset index when a new latest text arrives
    setCurrentIndex(0); 

    const timer = setInterval(() => {
      setCurrentIndex((prev) => {
        if (prev < text.length) return prev + 1;
        
        clearInterval(timer);
        return prev;
      });
    }, 20); // 20ms per character

    return () => clearInterval(timer);
  }, [text, isLatest]);

  // Safely slice the original string to prevent any duplication
  return <span>{text.substring(0, currentIndex)}</span>;
});

// --- MAIN LOG COMPONENT ---
const AgentLog = () => {
  const scrollRef = useRef(null);

  // 1. Strict Subscription
  const agentLog = useArkStore(useShallow((state) => state.agentLog));

  // 2. Data Memoization (Allow history to build up so scrolling activates)
  const displayLogs = useMemo(() => {
    // Slicing to 100 keeps performance high while giving you plenty of scrollable history.
    // We removed the .slice(-8) that was deleting your old logs!
    return agentLog.slice(-100).map((log) => ({
      ...log,
      truncatedMsg: log.message.length > 45 
        ? log.message.substring(0, 45) + '...' 
        : log.message
    }));
  }, [agentLog]);

  // 3. Auto-scroll logic
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [agentLog.length]);

  // Styling helper
  const getAgentColor = (type) => {
    switch (type) {
      case 'system': return 'text-cyan-400';
      case 'critical': return 'text-rose-500';
      case 'agent': return 'text-green-400';
      default: return 'text-slate-300';
    }
  };

  return (
    <div className="flex flex-col bg-ark-panel/90 border border-ark-border rounded-sm w-full h-full max-w-md backdrop-blur-md z-50 pointer-events-auto">
      
      {/* Header */}
      <div className="px-3 pt-2 pb-1 border-b border-ark-border">
        <h3 className="font-mono text-[10px] text-ark-silver tracking-widest font-semibold uppercase">
          AGENTIC LOGS // CRITICAL PATH
        </h3>
      </div>

      {/* Wrapper for Gradients and Scrolling */}
      <div className="relative flex-1 overflow-hidden flex flex-col">
        
        {/* Top/Bottom Fade Gradients */}
        <div className="absolute top-0 left-0 right-0 h-4 bg-gradient-to-b from-[#0B0F19] to-transparent z-10 pointer-events-none"></div>
        <div className="absolute bottom-0 left-0 right-0 h-4 bg-gradient-to-t from-[#0B0F19] to-transparent z-10 pointer-events-none"></div>

        {/* Log Container with Stealth Scrollbar */}
        <div 
          ref={scrollRef}
          className="absolute inset-0 p-3 pr-2 space-y-3 overflow-y-auto font-mono text-xs [&::-webkit-scrollbar]:w-1 [&::-webkit-scrollbar-track]:bg-transparent [&::-webkit-scrollbar-thumb]:bg-cyan-900/40 hover:[&::-webkit-scrollbar-thumb]:bg-cyan-400/80 [&::-webkit-scrollbar-thumb]:rounded-full"
        >
          {displayLogs.length === 0 && (
            <div className="text-ark-silver/50 italic text-[10px] mt-2 animate-pulse">Awaiting telemetry...</div>
          )}

          {displayLogs.map((entry, idx) => {
            const isLatest = idx === displayLogs.length - 1;
            const agentColor = getAgentColor(entry.type);

            return (
              // Changed to flex-col so the message drops to the next line
              <div key={`${entry.timestamp}-${idx}`} className="flex flex-col leading-tight">
                
                {/* Line 1: Timestamp & Agent Name */}
                <div className="flex items-start space-x-2">
                  <span className="text-cyan-400 opacity-80 shrink-0">
                    [{entry.timestamp}]
                  </span>
                  <span className={`${agentColor} font-bold shrink-0`}>
                    {entry.agent}:
                  </span>
                </div>
                
                {/* Line 2: The Log Message */}
                {/* Added mt-0.5 for a tiny gap, and removed break-all for standard wrapping */}
                <div className="text-slate-300 break-words mt-0.5 pl-[2px]">
                  <TypewriterText 
                    text={entry.truncatedMsg} 
                    isLatest={isLatest} 
                  />
                </div>
                
              </div>
            );
          })}
        </div>
        
      </div>
    </div>
  );
};

export default memo(AgentLog);