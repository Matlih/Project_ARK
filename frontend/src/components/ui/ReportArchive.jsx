import React, { memo } from 'react';
import { useArkStore } from '../../store/arkStore';
import { useShallow } from 'zustand/react/shallow';
import { printReportText } from './NDRRMCReport';

const ReportArchive = () => {
  const {
    isArchiveOpen,
    setArchiveOpen,
    reportArchive,
    deleteArchivedReport,
    addReportToArchive,
  } = useArkStore(
    useShallow((state) => ({
      isArchiveOpen:        state.isArchiveOpen,
      setArchiveOpen:       state.setArchiveOpen,
      reportArchive:        state.reportArchive,
      deleteArchivedReport: state.deleteArchivedReport,
      addReportToArchive:   state.addReportToArchive,
    }))
  );

  if (!isArchiveOpen) return null;

  // Resolve display text from either string or {en, fil} format
  const resolveText = (reportData, lang = 'EN') => {
    if (typeof reportData === 'object' && reportData !== null) {
      return lang === 'FIL' ? (reportData.fil || reportData.en || '') : (reportData.en || '');
    }
    return reportData || '';
  };

  // Extract a short title from the first non-empty line of the EN report
  const getTitle = (reportData) => {
    const text = resolveText(reportData, 'EN');
    const firstLine = text.split('\n').find((l) => l.trim().length > 0) || 'NDRRMC SITUATION REPORT';
    return firstLine.length > 60 ? firstLine.slice(0, 57) + '...' : firstLine;
  };

  const handleCopy = (reportData) => {
    navigator.clipboard.writeText(resolveText(reportData, 'EN'));
  };

  const handlePrint = (reportData) => {
    printReportText(resolveText(reportData, 'EN'));
  };

  /**
   * Before loading an archived report into the main view, save any currently-active
   * report so it isn't lost when ndrrmcReport is overwritten.
   */
  const handleView = (reportData) => {
    const { ndrrmcReport, ndrrmcReportFil } = useArkStore.getState();

    if (ndrrmcReport) {
      const enText  = typeof ndrrmcReport === 'object' ? ndrrmcReport.en  : ndrrmcReport;
      const filText = typeof ndrrmcReport === 'object' ? ndrrmcReport.fil : (ndrrmcReportFil || '');
      addReportToArchive({ en: enText, fil: filText });
    }

    useArkStore.setState({ ndrrmcReport: reportData, isReportVisible: true });
    setArchiveOpen(false);
  };

  return (
    <div className="fixed inset-0 z-[200] bg-[#0B0F19]/80 backdrop-blur-sm flex items-center justify-center p-6">
      <div className="bg-ark-panel w-full max-w-3xl border border-ark-border rounded-sm flex flex-col shadow-2xl max-h-[80vh]">

        {/* Header */}
        <div className="flex justify-between items-center p-4 border-b border-ark-border">
          <div>
            <h2 className="font-mono text-cyan-400 tracking-widest font-bold">INTELLIGENCE ARCHIVE</h2>
            <p className="font-mono text-ark-silver text-xs mt-0.5">
              {reportArchive.length} report{reportArchive.length !== 1 ? 's' : ''} stored
            </p>
          </div>
          <button
            onClick={() => setArchiveOpen(false)}
            className="text-ark-silver hover:text-rose-500 font-bold text-lg"
          >
            ✕
          </button>
        </div>

        {/* Report List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {reportArchive.length === 0 ? (
            <p className="text-ark-silver font-mono text-sm text-center py-10">
              No reports archived. Close an active report to save it.
            </p>
          ) : (
            reportArchive.map((item) => (
              <div
                key={item.id}
                className="border border-ark-border bg-[#0B0F19]/50 p-3 flex justify-between items-start group hover:border-cyan-400/40 transition-colors"
              >
                <div className="flex flex-col gap-0.5 min-w-0 pr-4">
                  <span className="font-mono text-sm text-white font-bold truncate">
                    {getTitle(item.data)}
                  </span>
                  <span className="font-mono text-xs text-ark-silver">
                    Archived: {item.timestamp}
                  </span>
                  {item.data.fil && (
                    <span className="font-mono text-[10px] text-cyan-700 tracking-widest">
                      EN + FIL available
                    </span>
                  )}
                </div>

                <div className="flex space-x-2 shrink-0">
                  <button
                    onClick={() => handleView(item.data)}
                    className="px-3 py-1 bg-slate-800 text-cyan-400 border border-slate-600 hover:border-cyan-400 font-mono text-xs rounded-sm transition-colors"
                  >
                    VIEW
                  </button>
                  <button
                    onClick={() => handleCopy(item.data)}
                    className="px-3 py-1 bg-slate-800 text-white border border-slate-600 hover:border-slate-400 font-mono text-xs rounded-sm transition-colors"
                  >
                    COPY
                  </button>
                  <button
                    onClick={() => handlePrint(item.data)}
                    className="px-3 py-1 bg-slate-800 text-white border border-slate-600 hover:border-slate-400 font-mono text-xs rounded-sm transition-colors"
                  >
                    PDF
                  </button>
                  <button
                    onClick={() => deleteArchivedReport(item.id)}
                    className="px-3 py-1 bg-slate-800 text-rose-500 border border-rose-900 hover:border-rose-500 hover:bg-rose-500/10 font-mono text-xs rounded-sm transition-colors"
                  >
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
