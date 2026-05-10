import React, { useState, useEffect, useMemo, memo } from 'react';
import { useArkStore } from '../../store/arkStore';
import { useShallow } from 'zustand/react/shallow';

export const printReportText = (textToPrint) => {
  const printWindow = window.open('', '_blank', 'width=800,height=600');
  printWindow.document.write(`
    <html>
      <head>
        <title>NDRRMC Report</title>
        <style>
          body { font-family: monospace; padding: 40px; color: black; line-height: 1.5; white-space: pre-wrap; }
          .header { font-weight: bold; font-size: 1.2em; border-bottom: 2px solid black; padding-bottom: 10px; margin-bottom: 20px; }
        </style>
      </head>
      <body>
        <div class="header">PROJECT ARK // OFFICIAL SITUATION REPORT</div>
        <div>${textToPrint}</div>
      </body>
    </html>
  `);
  printWindow.document.close();
  printWindow.focus();
  setTimeout(() => {
    printWindow.print();
    printWindow.close();
  }, 250);
};

const NDRRMCReport = () => {
  const {
    ndrrmcReport,
    ndrrmcReportFil,
    isReportVisible,
    setReportVisible,
    addReportToArchive,
    reportLanguage,
    setReportLanguage,
  } = useArkStore(
    useShallow((state) => ({
      ndrrmcReport:      state.ndrrmcReport,
      ndrrmcReportFil:   state.ndrrmcReportFil,
      isReportVisible:   state.isReportVisible,
      setReportVisible:  state.setReportVisible,
      addReportToArchive: state.addReportToArchive,
      reportLanguage:    state.reportLanguage,
      setReportLanguage: state.setReportLanguage,
    }))
  );

  const [displayedText, setDisplayedText] = useState('');
  const [copied, setCopied] = useState(false);

  /**
   * Resolve the correct display text given the current language.
   * ndrrmcReport can be:
   *   - string  → EN text (live/mock pipeline output)
   *   - {en, fil} object → loaded from Intelligence Archive
   */
  const targetText = useMemo(() => {
    if (!ndrrmcReport && !ndrrmcReportFil) return '';

    // Archive-loaded: stored as normalized {en, fil} object
    if (typeof ndrrmcReport === 'object' && ndrrmcReport !== null) {
      return reportLanguage === 'EN'
        ? (ndrrmcReport.en || '')
        : (ndrrmcReport.fil || ndrrmcReport.en || '');
    }

    // Live / mock: ndrrmcReport = EN string, ndrrmcReportFil = FIL string
    return reportLanguage === 'EN'
      ? (ndrrmcReport || '')
      : (ndrrmcReportFil || ndrrmcReport || '');
  }, [ndrrmcReport, ndrrmcReportFil, reportLanguage]);

  // Typewriter effect — re-runs whenever targetText changes (language switch or new report)
  useEffect(() => {
    if (!targetText || !isReportVisible) return;
    setDisplayedText('');
    let i = 0;
    const intervalMs = Math.max(10, Math.floor(3000 / targetText.length));
    const timer = setInterval(() => {
      if (i < targetText.length) {
        setDisplayedText((prev) => prev + targetText.charAt(i));
        i++;
      } else {
        clearInterval(timer);
      }
    }, intervalMs);
    return () => clearInterval(timer);
  }, [targetText, isReportVisible]);

  const handleCopy = () => {
    navigator.clipboard.writeText(targetText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  /**
   * Archive the current report (both EN + FIL) before dismissing.
   * addReportToArchive deduplicates, so re-archiving an already-saved report is a no-op.
   */
  const handleClose = () => {
    if (ndrrmcReport) {
      const enText  = typeof ndrrmcReport === 'object' ? ndrrmcReport.en  : ndrrmcReport;
      const filText = typeof ndrrmcReport === 'object' ? ndrrmcReport.fil : (ndrrmcReportFil || '');
      addReportToArchive({ en: enText, fil: filText });
    }
    setReportVisible(false);
  };

  const renderLines = () =>
    displayedText.split('\n').map((line, idx) => {
      let colorClass = 'text-slate-300 text-xs';
      if (line.includes('NDRRMC') || line.includes('DRRMC')) colorClass = 'text-white font-bold text-sm';
      else if (line.includes('₱') || line.includes('PHP')) colorClass = 'text-amber-400 font-mono';
      else if (line.includes('PRIORITY') || line.includes('PRIYORIDAD')) colorClass = 'text-rose-400 font-bold';
      return (
        <div key={idx} className={`${colorClass} min-h-[1rem] leading-tight`}>
          {line}
        </div>
      );
    });

  return (
    <div
      className={`absolute right-4 top-20 w-80 max-h-[70vh] flex flex-col bg-ark-panel/95 border border-ark-border rounded-sm backdrop-blur-md z-40 transition-transform duration-400 ease-in-out ${
        isReportVisible ? 'translate-x-0' : 'translate-x-[150%]'
      }`}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-ark-border">
        <h2 className="font-mono text-xs text-ark-silver tracking-widest font-bold">
          NDRRMC REPORT
        </h2>
        <div className="flex space-x-3">
          <button
            onClick={handleCopy}
            className="text-ark-silver hover:text-cyan-400 transition-colors"
            title="Copy"
          >
            {copied ? '✓' : '📋'}
          </button>
          {/* Close: archives report before dismissing */}
          <button
            onClick={handleClose}
            className="text-ark-silver hover:text-rose-500 font-bold transition-colors"
            title="Close & save to archive"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Body */}
      <div className="p-4 overflow-y-auto flex-1 font-mono">
        <div className="space-y-1">{renderLines()}</div>
        {displayedText.length < targetText.length && (
          <span className="inline-block w-2 h-3 bg-cyan-400 animate-pulse" />
        )}
      </div>

      {/* Footer — language toggle + download */}
      <div className="p-3 border-t border-ark-border flex items-center justify-between bg-[#0B0F19]/50">
        <div className="flex space-x-1">
          {['EN', 'FIL'].map((lang) => (
            <button
              key={lang}
              onClick={() => setReportLanguage(lang)}
              className={`px-2 py-0.5 text-[10px] font-mono border rounded-sm transition-colors ${
                reportLanguage === lang
                  ? 'bg-cyan-400/20 text-cyan-400 border-cyan-400'
                  : 'text-ark-silver border-ark-border hover:border-ark-silver'
              }`}
            >
              {lang}
            </button>
          ))}
        </div>
        <button
          onClick={() => printReportText(targetText)}
          className="px-3 py-1 text-[10px] font-mono text-white bg-slate-800 border border-slate-600 hover:border-cyan-400 hover:text-cyan-400 transition-colors rounded-sm"
        >
          DOWNLOAD PDF
        </button>
      </div>
    </div>
  );
};

export default memo(NDRRMCReport);
