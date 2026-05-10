import React, { useState, useEffect, memo } from 'react';

// --- NATIVE TYPEWRITER EFFECT (IDEMPOTENT FIX) ---
const TypewriterLine = ({ text, delay = 0, speed = 25 }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [start, setStart] = useState(false);

  // 1. Handle the initial startup delay
  useEffect(() => {
    const timer = setTimeout(() => setStart(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  // 2. Safely increment the index
  useEffect(() => {
    if (!start) return;
    
    const interval = setInterval(() => {
      setCurrentIndex((prev) => {
        if (prev < text.length) return prev + 1;
        
        clearInterval(interval);
        return prev;
      });
    }, speed);
    
    return () => clearInterval(interval);
  }, [text, start, speed]);

  // 3. Render a clean slice of the original string
  return <span>{text.substring(0, currentIndex)}</span>;
};

const BootSequence = ({ onComplete }) => {
  const [progress, setProgress] = useState(0);
  const [isFadingOut, setIsFadingOut] = useState(false);
  const [visibleLogs, setVisibleLogs] = useState(0);
  
  // New State: Gatekeeper for the manual click
  const [isReady, setIsReady] = useState(false);

  const BOOT_LOGS = [
    "> Initializing AMD ROCm 6.x runtime...",
    "> Loading MI300X parallel stream context...",
    "> Connecting to NASA EONET feed...",
    "> Mounting Prithvi-100M analysis layer...",
    "> LangGraph mission control: ONLINE",
    "> PhilSA geospatial protocol: ACTIVE"
  ];

  useEffect(() => {
    // 1. Progress Bar Animation (0 to 100 over 2500ms)
    const startTime = Date.now();
    const duration = 2500;
    
    const progressInterval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const p = Math.min((elapsed / duration) * 100, 100);
      setProgress(p);
      if (elapsed >= duration) clearInterval(progressInterval);
    }, 16); 

    // 2. Staggered Log Appearance (~300ms between each line)
    const logInterval = setInterval(() => {
      setVisibleLogs((prev) => Math.min(prev + 1, BOOT_LOGS.length));
    }, 300);

    // 3. Unlock the System (at 2.5s)
    const readyTimeout = setTimeout(() => {
      setIsReady(true);
    }, 2500);

    return () => {
      clearInterval(progressInterval);
      clearInterval(logInterval);
      clearTimeout(readyTimeout);
    };
  }, [BOOT_LOGS.length]);

  // Handle the manual entry click
  const handleEnterSystem = () => {
    if (!isReady) return;
    setIsFadingOut(true);
    
    // 1. Play the boot initialization sound
    new Audio('/initialize.mp3').play().catch(e => console.log("Audio blocked:", e));
    
    // 2. Wake up J.A.R.V.I.S.
    window.dispatchEvent(new CustomEvent('jarvis-trigger', { 
      detail: "Welcome to Project Ark: The Geospatial Protocol for Strategic Disaster Kinematics, developed by Matlih. Geospatial intelligence protocol engaged."
    }));

    setTimeout(() => {
      if (onComplete) onComplete();
    }, 500);
  };
  return (
    <div 
      className={`fixed inset-0 z-[100] bg-[#0B0F19] flex flex-col items-center justify-center transition-opacity duration-500 ease-in-out pointer-events-auto ${
        isFadingOut ? 'opacity-0' : 'opacity-100'
      }`}
    >
      {/* Centered Content Block */}
      <div className="flex flex-col items-center w-full max-w-2xl px-6">
        
        <h1 className="text-4xl font-mono font-bold text-white tracking-[0.2em] mb-2">
          PROJECT ARK
        </h1>
        
        <div className="h-4 mb-12">
          <p className="text-xs font-mono text-ark-silver tracking-[0.4em] text-center">
            <TypewriterLine text="GEOSPATIAL PROTOCOL FOR STRATEGIC DISASTER KINEMATICS" delay={0} speed={30} />
          </p>
        </div>

        {/* Fake Boot Log */}
        <div className="w-full flex flex-col space-y-1.5 h-32 pl-8 border-l border-ark-border/50 font-mono text-xs text-cyan-400/70 mb-10">
          {BOOT_LOGS.map((log, index) => (
            index < visibleLogs && (
              <div key={index} className="flex">
                <TypewriterLine text={log} delay={0} speed={15} />
              </div>
            )
          ))}
        </div>

        {/* The Gatekeeper Button */}
        <button
          onClick={handleEnterSystem}
          disabled={!isReady}
          className={`font-mono text-sm tracking-[0.3em] px-8 py-3 rounded-sm border transition-all duration-300 ${
            isReady 
              ? 'border-cyan-400 text-cyan-400 hover:bg-cyan-400/10 hover:shadow-[0_0_15px_rgba(34,211,238,0.3)] cursor-pointer animate-pulse' 
              : 'border-slate-800 text-slate-600 cursor-not-allowed'
          }`}
        >
          {isReady ? 'INITIALIZE SYSTEM' : 'SYSTEM BOOTING...'}
        </button>

      </div>

      {/* Absolute Bottom Progress Bar */}
      <div className="absolute bottom-0 left-0 w-full h-[1px] bg-slate-800">
        <div 
          className="h-full bg-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.5)] transition-all ease-linear"
          style={{ width: `${progress}%`, transitionDuration: '16ms' }}
        />
      </div>
    </div>
  );
};

export default memo(BootSequence);