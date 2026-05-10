import { MOCK_REGIONS } from '../data/mockPipelineData'
import { useARKStore } from '../store/arkStore'

const delay = ms => new Promise(r => setTimeout(r, ms))

export async function runMockPipeline(region = "Philippines: Luzon") {
  const data = MOCK_REGIONS[region] || MOCK_REGIONS["Philippines: Luzon"]
  const store = useARKStore.getState()

  store.setStatus('RUNNING')
  store.setGlobeTarget(data.event.coords)

  // Simulate gate results with realistic timing
  for (const gate of data.gateResults) {
    await delay(gate.processing_ms * 3) // slow down for theater
    store.addGateResult(gate)
    store.addAgentLog({
      timestamp: new Date().toLocaleTimeString(),
      agent: gate.gate_name,
      message: `${gate.status}: ${gate.reason}`,
      type: gate.status === 'FAIL' ? 'critical' : 'system'
    })
    if (gate.compute_saved_hrs > 0) {
      store.updateMetrics({
        totalComputeSavedHrs: store.totalComputeSavedHrs + gate.compute_saved_hrs,
        totalComputeSavedUsd: store.totalComputeSavedUsd + (gate.compute_saved_hrs * 1.99),
        latencyMs: gate.processing_ms
      })
    }
  }

  // Simulate agent chain
  for (const log of data.agentLogs) {
    await delay(1000)
    store.addAgentLog({
      timestamp: new Date().toLocaleTimeString(),
      ...log
    })
    if (log.coords) {
      store.setGlobeTarget({ lat: log.coords[1], lon: log.coords[0],
                             label: 'ECONOMIC IMPACT ZONE' })
    }
  }

  // Final completion
  await delay(1000)
  store.updateMetrics({
    totalPesoLoss: data.pipelineComplete.total_peso_loss,
    totalComputeSavedUsd: data.pipelineComplete.total_compute_saved_usd
  })
  store.setState({
    ndrrmcReport: data.pipelineComplete.report,
    ndrrmcReportFil: data.pipelineComplete.report_fil,
    pipelineStatus: 'COMPLETE'
  })
}