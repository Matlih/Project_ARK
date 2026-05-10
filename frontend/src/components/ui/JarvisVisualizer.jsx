import React, { useEffect, useRef } from 'react';
import { useJarvisVoice } from '../../hooks/useJarvisVoice';
import { useArkStore } from '../../store/arkStore';
import { useShallow } from 'zustand/react/shallow';

// Keywords that indicate a raw data payload or report body — J.A.R.V.I.S. must not read these.
const REPORT_BLOCKLIST = /report|result|ndrrmc|sitrep|buod|epekto|rekomendasyon|\₱|\d{5,}/i;

export const JarvisVisualizer = () => {
  const { speak, isSpeaking, isMuted, toggleMute } = useJarvisVoice();

  const pipelineStatus = useArkStore(useShallow(state => state.pipelineStatus));
  const agentLog       = useArkStore(useShallow(state => state.agentLog));

  const prevStatus         = useRef(pipelineStatus);
  const lastProcessedIndex = useRef(0);
  const isSystemUnlocked   = useRef(false);
  const processStartTime   = useRef(null);

  // 1. Boot Sequence Unlock — fires once from BootSequence component
  useEffect(() => {
    const handleJarvisEvent = (e) => {
      isSystemUnlocked.current = true;
      if (window.speechSynthesis) window.speechSynthesis.cancel();
      if (e.detail) speak(e.detail, { priority: 'high' });
    };

    window.addEventListener('jarvis-trigger', handleJarvisEvent);
    return () => window.removeEventListener('jarvis-trigger', handleJarvisEvent);
  }, [speak]);

  // 2. Pipeline Status Milestones — high priority; always cut prior speech
  useEffect(() => {
    if (!isSystemUnlocked.current) return;

    if (pipelineStatus === 'RUNNING' && prevStatus.current !== 'RUNNING') {
      processStartTime.current = Date.now();
      speak('Allocating 192 gigabytes of H B M 3 memory. Pipeline engaged.', { priority: 'high' });

    } else if (pipelineStatus === 'COMPLETE' && prevStatus.current !== 'COMPLETE') {
      let timeString = 'optimal';
      if (processStartTime.current) {
        const elapsed = ((Date.now() - processStartTime.current) / 1000).toFixed(1);
        timeString = `${elapsed} seconds`;
      }
      speak(`Analysis complete in ${timeString}. Situation report generated and ready for review.`, { priority: 'high' });

    } else if (pipelineStatus === 'IDLE' && prevStatus.current !== 'IDLE') {
      speak('System reset. Awaiting new coordinates.', { priority: 'high' });
    }

    prevStatus.current = pipelineStatus;
  }, [pipelineStatus, speak]);

  // 3. Agent Log — PROCESS ONLY: announce stages, never read report bodies or raw data
  useEffect(() => {
    if (agentLog.length === 0) {
      lastProcessedIndex.current = 0;
      return;
    }

    if (agentLog.length > lastProcessedIndex.current) {
      const newLogs = agentLog.slice(lastProcessedIndex.current);

      newLogs.forEach(log => {
        if (!isSystemUnlocked.current) return;

        const msg = (log.message || '').toLowerCase();

        // Hard block: never speak report bodies, result payloads, or raw numeric data
        if (REPORT_BLOCKLIST.test(log.message || '')) return;

        // Critical failure — cut through immediately
        if (msg.includes('failed') || msg.includes('error')) {
          speak(
            'Critical error. Orchestrator backend unreachable. N A S A E O N E T and E S A Copernicus uplinks have failed.',
            { priority: 'high' }
          );
          return;
        }

        // Gate stage announcements — high priority cuts prior utterance
        if (msg.includes('gate_1') || msg.includes('gate 1')) {
          speak('Initializing Gate 1. Quality Assurance protocol engaged.', { priority: 'high' });
        } else if (msg.includes('gate_2') || msg.includes('gate 2')) {
          speak('Initializing Gate 2. Atmospheric analysis commencing.', { priority: 'high' });
        } else if (msg.includes('gate_3') || msg.includes('gate 3')) {
          speak('Initializing Gate 3. Spectral validation in progress.', { priority: 'high' });

        // Agent stage cues — queue naturally
        } else if (msg.includes('eonet') || msg.includes('sentinel') || msg.includes('prithvi')) {
          speak('Satellite uplink established. Routing imagery to M I 300 X clusters.');
        } else if (msg.includes('damage_assessment') || msg.includes('qwen')) {
          speak('Scanning target zone for structural anomalies.');
        } else if (msg.includes('economic_valuation') || msg.includes('xgboost')) {
          speak('Calculating economic impact and asset vulnerability.');
        } else if (msg.includes('insurance')) {
          speak('Cross-referencing insurance exposure matrix.');
        } else if (msg.includes('recovery')) {
          speak('Mapping recovery corridors and priority response zones.');
        } else if (msg.includes('ndrrmc_officer') || msg.includes('ndrrmc officer')) {
          speak('Compiling National Disaster Risk Reduction situation report.');
        }
      });

      lastProcessedIndex.current = agentLog.length;
    }
  }, [agentLog, speak]);

  return (
    <div className="flex flex-col items-center justify-center p-6 min-h-[200px]">

      <div
        onClick={toggleMute}
        className="relative flex items-center justify-center w-28 h-28 cursor-pointer group"
      >
        {/* Ambient Base Glow */}
        <div className={`absolute inset-0 rounded-full transition-opacity duration-700 ${
          isMuted ? 'opacity-0' : 'bg-cyan-900/20 blur-xl'
        }`} />

        {/* Active Speaking Pulses */}
        {isSpeaking && !isMuted && (
          <>
            <div className="absolute inset-2 rounded-full border border-cyan-400 animate-ping opacity-75" style={{ animationDuration: '1s' }} />
            <div className="absolute inset-[-10px] rounded-full border border-cyan-600 animate-ping opacity-40" style={{ animationDelay: '150ms', animationDuration: '1.5s' }} />
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
          }`} />
        </div>

        {/* Mute Indicator */}
        {isMuted && (
          <div className="absolute -bottom-6 text-[10px] tracking-widest text-rose-500/70 font-mono">
            AUDIO_OFFLINE
          </div>
        )}
      </div>

    </div>
  );
};
