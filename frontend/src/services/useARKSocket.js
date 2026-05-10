import { useEffect, useRef } from 'react';
import ReconnectingWebSocket from 'reconnecting-websocket';
import { useArkStore } from '../store/arkStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://165.245.138.122:8000';
const WS_URL  = import.meta.env.VITE_WS_URL  || 'ws://165.245.138.122:8000/ws'; // fixed: removed stray 't'

// When true, always use the high-fidelity mock regardless of backend reachability
const SIMULATION_MODE = import.meta.env.VITE_SIMULATION_MODE === 'true';

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
 * Triggers the ARK processing pipeline. Routes between Simulation, Live, and Mock environments.
 * @param {string} region - Target region for analysis
 */
export async function triggerPipeline(region = 'Philippines: Luzon') {
  const store = useArkStore.getState();
  store.setStatus('RUNNING');

  // Route 1: Sovereign Simulation Mode — always wins
  if (SIMULATION_MODE || store.backendMode === 'mock') {
    console.log('[ARK] Sovereign Simulation Mode — executing high-fidelity mock.');
    const { runMockPipeline } = await import('./mockPipeline.js');
    runMockPipeline(region);
    return;
  }

  // Route 2: Live Execution with mid-flight fallback
  try {
    const encodedRegion = encodeURIComponent(region);
    const response = await fetch(`${API_URL}/demo?region=${encodedRegion}`, { method: 'GET' });
    if (!response.ok) throw new Error('Live endpoint rejected the request.');
  } catch (error) {
    console.warn('[ARK] Live trigger failed — falling back to mock pipeline.', error);
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
    await fetch(`${API_URL}/reset`, { method: 'GET' }).catch(() => {});
  } finally {
    store.resetAll();
  }
};

/**
 * Core WebSocket Hook. Handles initial mount health-check and manages the telemetry stream.
 */
export const useARKSocket = () => {
  const socketRef = useRef(null);

  useEffect(() => {
    let isMounted = true;
    let rws = null;

    const initializeSystem = async () => {

      // Sovereign Simulation Mode bypasses the health check entirely
      if (SIMULATION_MODE) {
        console.log('[ARK] SOVEREIGN SIMULATION MODE ACTIVE — backend check skipped.');
        useArkStore.setState({ backendMode: 'mock' });
        return;
      }

      const health = await checkBackendHealth();
      if (!isMounted) return;

      if (health.online && health.mode === 'live') {
        console.log('[ARK] MI300X cloud active. Establishing real-time telemetry.');
        useArkStore.setState({ backendMode: 'live' });

        rws = new ReconnectingWebSocket(WS_URL, [], {
          maxRetries: Infinity,
          connectionTimeout: 4000,
          maxEnqueuedMessages: 100,
        });

        socketRef.current = rws;

        rws.addEventListener('open', () => {
          console.log('[ARK] WebSocket connection established.');
        });

        rws.addEventListener('close', () => {
          console.warn('[ARK] WebSocket disconnected — ReconnectingWebSocket will retry.');
        });

        rws.addEventListener('message', (event) => {
          try {
            const payload = JSON.parse(event.data);
            if (!payload || typeof payload !== 'object') return;

            const { type, data } = payload;
            const store = useArkStore.getState();
            const timestamp = new Date().toLocaleTimeString();

            switch (type) {

              case 'ping':
                store.updateMetrics({ latencyMs: data.latency_ms });
                break;

              case 'gate_result':
                store.addGateResult(data);
                store.updateMetrics({
                  computeSavedHrs: data.compute_saved_hrs || 0,
                  computeSavedUsd: (data.compute_saved_hrs || 0) * 1.99,
                  analystHrsSaved: (data.compute_saved_hrs || 0) * 2.0,
                });
                store.addAgentLog({
                  timestamp,
                  agent: data.gate_name || 'System Gate',
                  message: `${data.status}: ${data.reason || 'Processed'}`,
                  type: data.status === 'FAIL' ? 'critical' : 'system',
                });
                break;

              case 'agent_update':
                store.addAgentLog({
                  timestamp,
                  agent: data.agent || 'Unknown Agent',
                  message: data.message || '',
                  type: 'agent',
                });
                // Globe zoom — match any agent name containing 'damage'
                if (
                  (data.agent || '').toLowerCase().includes('damage') &&
                  Array.isArray(data.coords) &&
                  data.coords.length >= 2
                ) {
                  store.setGlobeTarget({
                    lat: data.coords[1],
                    lon: data.coords[0],
                    label: 'ECONOMIC IMPACT ZONE',
                  });
                }
                break;

              case 'pipeline_complete':
                store.setStatus('COMPLETE');
                store.updateMetrics({ pesoLoss: data.total_peso_loss || 0 });
                // Archive with both languages so the archive viewer supports EN/FIL toggle
                store.addReportToArchive({ en: data.report || '', fil: data.report_fil || '' });
                useArkStore.setState({
                  ndrrmcReport:    data.report     || null,
                  ndrrmcReportFil: data.report_fil || null,
                  isReportVisible: true,
                });
                break;

              case 'error':
                store.setStatus('ERROR');
                store.addAgentLog({
                  timestamp,
                  agent: 'SYSTEM',
                  message: data.message || 'Unidentified pipeline exception.',
                  type: 'critical',
                });
                break;

              default:
                console.warn(`[ARK] Unhandled message type: ${type}`);
            }
          } catch (error) {
            console.error('[ARK] Failed to parse WebSocket payload:', error, 'Raw:', event.data);
          }
        });

        rws.addEventListener('error', (err) => {
          console.error('[ARK] WebSocket error:', err);
        });

      } else {
        console.warn('[ARK] Backend unreachable — engaging Zero-Downtime Mock Framework.');
        useArkStore.setState({ backendMode: 'mock' });
        try {
          const { initMockMode } = await import('./mockPipeline.js');
          if (initMockMode) initMockMode();
        } catch {
          // initMockMode is optional
        }
      }
    };

    initializeSystem();

    return () => {
      isMounted = false;
      if (rws) rws.close();
    };
  }, []);

  return socketRef.current;
};
