import { create } from 'zustand';

const initialState = {
  // Connection mode: 'mock' | 'live'
  backendMode: 'mock',

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
  ndrrmcReportFil: null,
  globeTarget: null,
  damageZones: [],

  // Report UI state
  isReportVisible: false,
  reportLanguage: 'EN', // 'EN' | 'FIL'

  // Intelligence Archive
  isArchiveOpen: false,
  reportArchive: [],

  // EONET Telemetry State
  eonetFeed: [],
};

export const useArkStore = create((set) => ({
  ...initialState,

  setStatus: (status) => set(() => ({ pipelineStatus: status })),

  addGateResult: (result) => set((state) => ({
    gateResults: [...state.gateResults, result],
  })),

  addAgentLog: (entry) => set((state) => ({
    agentLog: [...state.agentLog, entry],
  })),

  updateMetrics: (metrics) => set((state) => ({
    totalComputeSavedHrs: state.totalComputeSavedHrs + (metrics.computeSavedHrs || 0),
    totalComputeSavedUsd: state.totalComputeSavedUsd + (metrics.computeSavedUsd || 0),
    totalAnalystHrsSaved: state.totalAnalystHrsSaved + (metrics.analystHrsSaved || 0),
    totalPesoLoss: state.totalPesoLoss + (metrics.pesoLoss || 0),
    latencyMs: metrics.latencyMs !== undefined ? metrics.latencyMs : state.latencyMs,
  })),

  setGlobeTarget: (target) => set(() => ({ globeTarget: target })),

  // --- REPORT UI ACTIONS ---
  setReportVisible: (visible) => set(() => ({ isReportVisible: visible })),

  setReportLanguage: (lang) => set(() => ({ reportLanguage: lang })),

  // --- INTELLIGENCE ARCHIVE ACTIONS ---
  setArchiveOpen: (isOpen) => set(() => ({ isArchiveOpen: isOpen })),

  /**
   * Appends a report to the Intelligence Archive.
   * Accepts either a plain string (EN only) or a {en, fil} object.
   * Deduplicates: skips if EN content matches the most-recent archive entry.
   */
  addReportToArchive: (reportData) => set((state) => {
    // Normalize to {en, fil} object for consistent archive storage
    const normalized =
      typeof reportData === 'object' && reportData !== null && 'en' in reportData
        ? reportData
        : { en: reportData || '', fil: '' };

    // Deduplicate: skip if EN content matches the latest archive entry
    const last = state.reportArchive[0];
    if (last && last.data.en && last.data.en === normalized.en) return {};

    return {
      reportArchive: [
        { id: Date.now(), data: normalized, timestamp: new Date().toLocaleTimeString() },
        ...state.reportArchive,
      ],
    };
  }),

  deleteArchivedReport: (id) => set((state) => ({
    reportArchive: state.reportArchive.filter((r) => r.id !== id),
  })),

  // --- EONET ACTIONS ---
  addEonetEvent: (event) => set((state) => ({
    eonetFeed: [event, ...state.eonetFeed].slice(0, 15),
  })),

  setEonetEvents: (events) => set(() => ({
    eonetFeed: events.slice(0, 15),
  })),

  resetAll: () => set(() => ({ ...initialState })),
}));
