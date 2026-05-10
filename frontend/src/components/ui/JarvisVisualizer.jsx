import React, { useEffect, useRef } from 'react';
import { useJarvisVoice } from '../../hooks/useJarvisVoice';
import { useArkStore } from '../../store/arkStore';
import { useShallow } from 'zustand/react/shallow';

export const JarvisVisualizer = () => {
  const { speak, isSpeaking, isMuted, toggleMute } = useJarvisVoice();
  
  const pipelineStatus = useArkStore(useShallow(state => state.pipelineStatus));
  const agentLog = useArkStore(useShallow(state => state.agentLog));
  
  const prevStatus = useRef(pipelineStatus);
  const lastProcessedIndex = useRef(0);
  const isSystemUnlocked = useRef(false);
  
  // NEW: Internal AI clock to track literal processing time
  const processStartTime = useRef(null);

  // 1. Listen for the Boot Sequence Unlock
  useEffect(() => {
    const handleJarvisEvent = (e) => {
      isSystemUnlocked.current = true;
      if (window.speechSynthesis) window.speechSynthesis.cancel();
      if (e.detail) speak(e.detail);
    };
    
    window.addEventListener('jarvis-trigger', handleJarvisEvent);
    return () => window.removeEventListener('jarvis-trigger', handleJarvisEvent);
  }, [speak]);

  // 2. Watch Pipeline Status Milestones
  useEffect(() => {
    if (!isSystemUnlocked.current) return;

    if (pipelineStatus === 'RUNNING' && prevStatus.current !== 'RUNNING') {
      // Start the internal stopwatch
      processStartTime.current = Date.now();
      speak("Allocating 192 gigabytes of H B M 3 memory. Pipeline engaged.");
      
    } else if (pipelineStatus === 'COMPLETE' && prevStatus.current !== 'COMPLETE') {
      // Stop the watch and calculate exact seconds to 1 decimal place
      let timeString = "optimal";
      if (processStartTime.current) {
        const elapsedSeconds = ((Date.now() - processStartTime.current) / 1000).toFixed(1);
        timeString = `${elapsedSeconds} seconds`;
      }
      
      speak(`Analysis complete in ${timeString}. Situation report generated and ready for review.`);
      
    } else if (pipelineStatus === 'IDLE' && prevStatus.current !== 'IDLE') {
      speak("System reset. Awaiting new coordinates.");
    }
    
    prevStatus.current = pipelineStatus;
  }, [pipelineStatus, speak]);

  // 3. Watch Agent Logs for Cinematic Keywords
  useEffect(() => {
    if (agentLog.length === 0) {
      lastProcessedIndex.current = 0;
      return;
    }

    if (agentLog.length > lastProcessedIndex.current) {
      const newLogs = agentLog.slice(lastProcessedIndex.current);
      
      newLogs.forEach(log => {
        if (!isSystemUnlocked.current) return;

        const msg = log.message.toLowerCase();
        
        // NEW: Critical Failure Interruption
        if (msg.includes('failed') || msg.includes('error')) {
          // Instantly cut off any ongoing speech (like the "Allocating..." line)
          if (window.speechSynthesis) window.speechSynthesis.cancel();
          
          speak("Critical error. Orchestrator backend unreachable. NASA EONET and ESA Copernicus uplinks have failed.");
          return; // Stop checking other conditions
        }
        
        if (msg.includes('eonet') || msg.includes('sentinel')) {
          speak("Satellite uplink established. Routing imagery to M I 300 X clusters.");
        } else if (msg.includes('damage_assessment')) {
          speak("Scanning target zone for structural anomalies.");
        } else if (msg.includes('economic_valuation')) {
          speak("Calculating economic impact and asset vulnerability.");
        }
      });
      
      lastProcessedIndex.current = agentLog.length;
    }
  }, [agentLog, speak]);

  return (
    <div className="flex flex-col items-center justify-center p-6 min-h-[200px]">
      
      {/* Visualizer Container */}
      <div 
        onClick={toggleMute}
        className="relative flex items-center justify-center w-28 h-28 cursor-pointer group"
      >
        {/* Ambient Base Glow */}
        <div className={`absolute inset-0 rounded-full transition-opacity duration-700 ${
          isMuted ? 'opacity-0' : 'bg-cyan-900/20 blur-xl'
        }`}></div>

        {/* Active Speaking Pulses */}
        {isSpeaking && !isMuted && (
          <>
            <div className="absolute inset-2 rounded-full border border-cyan-400 animate-ping opacity-75" style={{ animationDuration: '1s' }}></div>
            <div className="absolute inset-[-10px] rounded-full border border-cyan-600 animate-ping opacity-40" style={{ animationDelay: '150ms', animationDuration: '1.5s' }}></div>
          </>
        )}

        {/* Core Hardware Circle */}
        <div className={`relative z-10 flex items-center justify-center w-14 h-14 rounded-full transition-all duration-300 ${
          isMuted 
            ? 'bg-slate-900/80 border-2 border-rose-900/40 shadow-[0_0_10px_rgba(159,18,57,0.2)] opacity-60' 
            : isSpeaking 
              ? 'bg-cyan-500 border-2 border-cyan-200 shadow-[0_0_40px_rgba(34,211,238,0.8)] scale-110' 
              : 'bg-slate-900 border-2 border-cyan-900/80 shadow-[0_0_20px_rgba(8,145,178,0.3)] group-hover:border-cyan-700'
        }`}>
          
          {/* Inner Optical Core */}
          <div className={`w-5 h-5 rounded-full transition-colors duration-300 ${
            isMuted 
              ? 'bg-rose-900/30' 
              : isSpeaking 
                ? 'bg-white shadow-[0_0_15px_rgba(255,255,255,1)]' 
                : 'bg-cyan-900/60'
          }`}></div>
        </div>
        
        {/* Mute Indicator Label */}
        {isMuted && (
          <div className="absolute -bottom-6 text-[10px] tracking-widest text-rose-500/70 font-mono">
            AUDIO_OFFLINE
          </div>
        )}
      </div>
      
    </div>
  );
};