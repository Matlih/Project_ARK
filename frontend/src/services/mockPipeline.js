import { MOCK_REGIONS } from '../data/mockPipelineData';
import { useArkStore } from '../store/arkStore';

const delay = ms => new Promise(r => setTimeout(r, ms));

export function initMockMode() {
  // No-op initializer — mock mode is activated by the store flag set in useARKSocket.
}

export async function runMockPipeline(region = 'Philippines: Luzon') {
  const data = MOCK_REGIONS[region] || MOCK_REGIONS['Philippines: Luzon'];
  const store = useArkStore.getState();

  store.setStatus('RUNNING');
  store.setGlobeTarget(data.event.coords);

  // Gate results with cinematic pacing
  for (const gate of data.gateResults) {
    await delay(gate.processing_ms * 3);
    store.addGateResult(gate);
    store.addAgentLog({
      timestamp: new Date().toLocaleTimeString(),
      agent: gate.gate_name,
      message: `${gate.status}: ${gate.reason}`,
      type: gate.status === 'FAIL' ? 'critical' : 'system',
    });
    if (gate.compute_saved_hrs > 0) {
      store.updateMetrics({
        computeSavedHrs: gate.compute_saved_hrs,
        computeSavedUsd: gate.compute_saved_hrs * 1.99,
        latencyMs: gate.processing_ms,
      });
    }
  }

  // Agent chain with 1-second pacing per log entry
  for (const log of data.agentLogs) {
    await delay(1000);
    store.addAgentLog({
      timestamp: new Date().toLocaleTimeString(),
      ...log,
    });
    if (log.coords) {
      store.setGlobeTarget({
        lat: log.coords[1],
        lon: log.coords[0],
        label: 'ECONOMIC IMPACT ZONE',
      });
    }
  }

  // Final pipeline completion
  await delay(1000);
  store.updateMetrics({
    pesoLoss: data.pipelineComplete.total_peso_loss,
  });
  // Archive with both languages immediately so the archive is populated even if
  // the user never manually closes the report modal.
  store.addReportToArchive({
    en:  data.pipelineComplete.report     || '',
    fil: data.pipelineComplete.report_fil || '',
  });
  useArkStore.setState({
    ndrrmcReport:    data.pipelineComplete.report,
    ndrrmcReportFil: data.pipelineComplete.report_fil,
    pipelineStatus:  'COMPLETE',
    isReportVisible: true,
  });
}
