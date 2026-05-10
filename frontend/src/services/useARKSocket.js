import { useEffect, useRef } from 'react';
import ReconnectingWebSocket from 'reconnecting-websocket';
import { useArkStore } from '../store/arkStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

/**
 * Pings the backend to verify the MI300X instance is online and returning 'live' status.
 * Aborts automatically after 3 seconds to prevent UI hanging.
 */
export async function checkBackendHealth() {
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 3000);
    const res = await fetch(`${API_URL}/health`, { signal: controller.signal });
    clearTimeout(timeout);
    
    if (!res.ok) return { online: false };
    return { online: true, ...(await res.json()) };
  } catch {
    return { online: false };
  }
}

/**
 * Triggers the ARK processing pipeline. Routes seamlessly between Live and Mock environments.
 * @param {string} region - Target region for analysis
 */
export async function triggerPipeline(region = 'Philippines') {
  const store = useArkStore.getState();
  const { backendMode } = store;
  
  store.setStatus('RUNNING');

  // Route 1: Clean Mock Execution
  if (backendMode === 'mock') {
    console.log('[ARK Architecture] Live backend bypassed. Executing synthetic pipeline (Mock Mode).');
    const { runMockPipeline } = await import('./mockPipeline.js');
    runMockPipeline(region);
    return;
  }

  // Route 2: Live Execution with Mid-Flight Fallback
  try {
    const response = await fetch(`${API_URL}/demo`, { method: 'GET' });
    if (!response.ok) throw new Error('Live endpoint rejected the request.');
  } catch (error) {
    console.warn('[ARK Architecture] Live trigger failed mid-flight, falling back to mock pipeline.', error);
    const { runMockPipeline } = await import('./mockPipeline.js');
    runMockPipeline(region);
  }
}

/**
 * Resets the backend session (if available) and wipes local state.
 */
export const resetSystem = async () => {
  const store = useArkStore.getState();
  
  try {
    // We swallow errors here because if the backend is down, we still want the UI to reset cleanly.
    await fetch(`${API_URL}/reset`, { method: 'GET' }).catch(() => {});
  } catch (error) {
    console.error('[ARK Architecture] Reset API Error:', error);
  } finally {
    store.resetAll();
  }
};

/**
 * Core WebSocket Hook. 
 * Handles initial mount detection and manages the telemetry stream.
 */
export const useARKSocket = () => {
  const socketRef = useRef(null);

  useEffect(() => {
    let isMounted = true; // 1. THE KILL-SWITCH FLAG
    let rws = null;

    const initializeSystem = async () => {
      const health = await checkBackendHealth();

      // 2. ABORT PROTOCOL: If React unmounted while we were waiting for the fetch, stop here!
      if (!isMounted) return;

      if (health.online && health.mode === 'live') {
        console.log('[ARK Architecture] MI300X cloud active. Establishing real-time telemetry.');
        useArkStore.setState({ backendMode: 'live' });

        rws = new ReconnectingWebSocket(WS_URL, [], {
          maxRetries: Infinity,
          connectionTimeout: 4000,
          maxEnqueuedMessages: 100,
        });

        socketRef.current = rws;

        rws.addEventListener('open', () => {
          console.log('[ARK Architecture] WebSocket connection established.');
        });

        rws.addEventListener('message', (event) => {
          try {
            const payload = JSON.parse(event.data);
            if (!payload || typeof payload !== 'object') return;

            const { type, data } = payload;
            const store = useArkStore.getState();
            const timestamp = new Date().toLocaleTimeString();

            switch (type) {
              
              // === THE LIVE HEARTBEAT CATCH ===
              case 'ping':
                store.updateMetrics({ latencyMs: data.latency_ms });
                break;

              case 'gate_result':
                store.addGateResult(data);
                store.updateMetrics({
                  computeSavedHrs: data.compute_saved_hrs || 0,
                  computeSavedUsd: (data.compute_saved_hrs || 0) * 1.99,
                  analystHrsSaved: (data.compute_saved_hrs || 0) * 2.0,
                  // We remove the latency override here so the heartbeat controls it exclusively
                });
                store.addAgentLog({
                  timestamp,
                  agent: data.gate_name || 'System Gate',
                  message: `${data.status}: ${data.reason || 'Processed'}`,
                  type: data.status === 'FAIL' ? 'critical' : 'system'
                });
                break;

              case 'agent_update':
                store.addAgentLog({
                  timestamp,
                  agent: data.agent || 'Unknown Agent',
                  message: data.message || '',
                  type: 'agent'
                });
                
                // === THE ROBUST STRING CATCH ===
                // Converts whatever Python sends to lowercase and looks for the keyword
                const agentName = (data.agent || '').toLowerCase();
                if (agentName.includes('damage') && Array.isArray(data.coords) && data.coords.length >= 2) {
                  store.setGlobeTarget({
                    lat: data.coords[1],
                    lon: data.coords[0],
                    label: 'ECONOMIC IMPACT ZONE'
                  });
                }
                break;
                
                // Triggers the 3D globe dive
                if (data.agent === 'damage_assessment_node' && Array.isArray(data.coords) && data.coords.length >= 2) {
                  store.setGlobeTarget({
                    lat: data.coords[1],
                    lon: data.coords[0],
                    label: 'ECONOMIC IMPACT ZONE'
                  });
                }
                break;

              case 'pipeline_complete':
                store.setStatus('COMPLETE');
                store.updateMetrics({ pesoLoss: data.total_peso_loss || 0 });
                store.addReportToArchive(data.report);
                
                useArkStore.setState({ 
                  ndrrmcReport: data.report || null,
                  isReportVisible: true 
                });
                break;

              case 'error':
                store.setStatus('ERROR');
                store.addAgentLog({
                  timestamp,
                  agent: 'SYSTEM',
                  message: data.message || 'Unidentified pipeline exception.',
                  type: 'critical'
                });
                break;

              default:
                console.warn(`[ARK Architecture] Unhandled message type intercepted: ${type}`);
            }
          } catch (error) {
            console.error('[ARK Architecture] Failed to parse WebSocket payload:', error, 'Raw Data:', event.data);
          }
        });

        rws.addEventListener('error', (err) => {
          console.error('[ARK Architecture] WebSocket encountered a connection error:', err);
        });

      } else {
        // BACKEND OFFLINE OR IN MOCK MODE
        console.warn('[ARK Architecture] Backend unreachable or not live. Engaging Zero-Downtime Mock Framework.');
        useArkStore.setState({ backendMode: 'mock' });
        
        try {
          // Dynamically import and initialize mock mode if the function is exposed in W.3
          const { initMockMode } = await import('./mockPipeline.js');
          if (initMockMode) initMockMode();
        } catch (e) {
          // Graceful catch if initMockMode isn't needed or exported
        }
      }
    };

    initializeSystem();

    return () => {
      isMounted = false; // 3. TRIP THE KILL-SWITCH ON UNMOUNT
      if (rws) rws.close();
    };
  }, []); // Empty dependency array ensures singleton connection per mount
  
  return socketRef.current;
};