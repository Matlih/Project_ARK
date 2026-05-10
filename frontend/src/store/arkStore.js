import { create } from 'zustand';

const initialState = {
  pipelineStatus: 'IDLE', 
  eventId: null,
  scenePath: null,
  gateResults: [], 
  ardCertified: false,
  totalComputeSavedHrs: 0,
  totalComputeSavedUsd: 0,
  totalAnalystHrsSaved: 0,
  totalPesoLoss: 0,
  latencyMs: 0,
  agentLog: [], 
  ndrrmcReport: null,
  globeTarget: null, 
  damageZones: [], 
  
  // Archive State
  isReportVisible: false,
  isArchiveOpen: false,
  reportArchive: [], 
  
  // EONET Telemetry State
  eonetFeed: [],
};

export const useArkStore = create((set) => ({
  ...initialState,

  setStatus: (status) => set(() => ({ pipelineStatus: status })),
  
  addGateResult: (result) => set((state) => ({ 
    gateResults: [...state.gateResults, result] 
  })),
  
  addAgentLog: (entry) => set((state) => ({ 
    agentLog: [...state.agentLog, entry] 
  })),
  
  updateMetrics: (metrics) => set((state) => ({
      totalComputeSavedHrs: state.totalComputeSavedHrs + (metrics.computeSavedHrs || 0),
      totalComputeSavedUsd: state.totalComputeSavedUsd + (metrics.computeSavedUsd || 0),
      totalAnalystHrsSaved: state.totalAnalystHrsSaved + (metrics.analystHrsSaved || 0),
      totalPesoLoss: state.totalPesoLoss + (metrics.pesoLoss || 0),
      latencyMs: metrics.latencyMs !== undefined ? metrics.latencyMs : state.latencyMs
  })),
  
  setGlobeTarget: (target) => set(() => ({ globeTarget: target })),
  
  // --- ARCHIVE ACTIONS ---
  setReportVisible: (visible) => set(() => ({ isReportVisible: visible })),
  
  setArchiveOpen: (isOpen) => set(() => ({ isArchiveOpen: isOpen })),
  
  addReportToArchive: (reportData) => set((state) => ({
    reportArchive: [{ id: Date.now(), data: reportData, timestamp: new Date().toLocaleTimeString() }, ...state.reportArchive]
  })),
  
  deleteArchivedReport: (id) => set((state) => ({
    reportArchive: state.reportArchive.filter(r => r.id !== id)
  })),

  // --- EONET ACTIONS ---
  addEonetEvent: (event) => set((state) => ({
    eonetFeed: [event, ...state.eonetFeed].slice(0, 15)
  })),
  
  // NEW: Bulk load for the initial fetch
  setEonetEvents: (events) => set(() => ({
    // Ensure we only keep the latest 15 to maintain UI performance
    eonetFeed: events.slice(0, 15)
  })),

  resetAll: () => set(() => ({ ...initialState }))
}));