import React, { memo } from 'react';
import { useArkStore } from '../../store/arkStore';
import { useShallow } from 'zustand/react/shallow';
import { printReportText } from './NDRRMCReport';

const ReportArchive = () => {
  const { isArchiveOpen, setArchiveOpen, reportArchive, deleteArchivedReport, setReportVisible } = useArkStore(
    useShallow((state) => ({
      isArchiveOpen: state.isArchiveOpen,
      setArchiveOpen: state.setArchiveOpen,
      reportArchive: state.reportArchive,
      deleteArchivedReport: state.deleteArchivedReport,
      setReportVisible: state.setReportVisible
    }))
  );

  if (!isArchiveOpen) return null;

  const handleCopy = (reportData) => {
    const text = typeof reportData === 'string' ? reportData : reportData.en;
    navigator.clipboard.writeText(text);
  };

  const handlePrint = (reportData) => {
    const text = typeof reportData === 'string' ? reportData : reportData.en;
    printReportText(text);
  };

  const handleView = (reportData) => {
    useArkStore.setState({ ndrrmcReport: reportData, isReportVisible: true });
    setArchiveOpen(false);
  };

  return (
    <div className="fixed inset-0 z-[200] bg-[#0B0F19]/80 backdrop-blur-sm flex items-center justify-center p-6">
      <div className="bg-ark-panel w-full max-w-3xl border border-ark-border rounded-sm flex flex-col shadow-2xl max-h-[80vh]">
        
        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b border-ark-border">
          <h2 className="font-mono text-cyan-400 tracking-widest font-bold">INTELLIGENCE ARCHIVE</h2>
          <button onClick={() => setArchiveOpen(false)} className="text-ark-silver hover:text-rose-500 font-bold text-lg">✕</button>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {reportArchive.length === 0 ? (
            <p className="text-ark-silver font-mono text-sm text-center py-10">No reports archived.</p>
          ) : (
            reportArchive.map((item) => (
              <div key={item.id} className="border border-ark-border bg-[#0B0F19]/50 p-3 flex justify-between items-center group hover:border-cyan-400/40 transition-colors">
                <div className="flex flex-col">
                  <span className="font-mono text-sm text-white font-bold">NDRRMC SITUATION REPORT</span>
                  <span className="font-mono text-xs text-ark-silver">Generated: {item.timestamp}</span>
                </div>
                
                <div className="flex space-x-2">
                  <button onClick={() => handleView(item.data)} className="px-3 py-1 bg-slate-800 text-cyan-400 border border-slate-600 hover:border-cyan-400 font-mono text-xs rounded-sm transition-colors">
                    VIEW
                  </button>
                  <button onClick={() => handleCopy(item.data)} className="px-3 py-1 bg-slate-800 text-white border border-slate-600 hover:border-slate-400 font-mono text-xs rounded-sm transition-colors">
                    COPY
                  </button>
                  <button onClick={() => handlePrint(item.data)} className="px-3 py-1 bg-slate-800 text-white border border-slate-600 hover:border-slate-400 font-mono text-xs rounded-sm transition-colors">
                    PDF
                  </button>
                  <button onClick={() => deleteArchivedReport(item.id)} className="px-3 py-1 bg-slate-800 text-rose-500 border border-rose-900 hover:border-rose-500 hover:bg-rose-500/10 font-mono text-xs rounded-sm transition-colors">
                    DELETE
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default memo(ReportArchive);