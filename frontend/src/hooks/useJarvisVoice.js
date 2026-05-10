import { useState, useEffect, useCallback, useRef } from 'react';
import { useArkStore } from '../store/arkStore';
import { useShallow } from 'zustand/react/shallow';

export const useJarvisVoice = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isMuted, setIsMuted]       = useState(false);
  const speakTimeout   = useRef(null);
  const lastSpokenText = useRef(''); // ANTI-SPAM tracker

  // Voice refs — populated once on mount, reused at speak time
  const enVoice  = useRef(null);
  const filVoice = useRef(null);

  // Subscribe to the global language preference so speak() picks the right locale
  const reportLanguage = useArkStore(useShallow((state) => state.reportLanguage));

  useEffect(() => {
    const loadVoices = () => {
      if (!window.speechSynthesis) return;
      const voices = window.speechSynthesis.getVoices();
      if (voices.length === 0) return;

      // English voice — prefer Google UK Male for the classic JARVIS timbre
      enVoice.current =
        voices.find((v) => v.name.includes('Google UK English Male')) ||
        voices.find((v) => v.lang === 'en-GB' && v.name.toLowerCase().includes('male')) ||
        voices.find((v) => v.lang === 'en-GB') ||
        voices[0];

      // Filipino / Tagalog voice — graceful fallback to EN voice if none found
      filVoice.current =
        voices.find((v) => v.lang === 'fil-PH') ||
        voices.find((v) => v.lang === 'tl-PH') ||
        voices.find((v) => v.name.toLowerCase().includes('filipino')) ||
        voices.find((v) => v.name.toLowerCase().includes('tagalog')) ||
        enVoice.current;
    };

    loadVoices();
    if (window.speechSynthesis?.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }
  }, []);

  const toggleMute = useCallback(() => {
    setIsMuted((prev) => {
      const next = !prev;
      if (next && window.speechSynthesis) {
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
      }
      return next;
    });
  }, []);

  /**
   * Speak a line of text.
   * @param {string} text
   * @param {{ priority?: 'high' }} options
   *   priority:'high' — cancels any current utterance immediately (stage starts, status changes).
   *   Default — queues naturally.
   *
   * Voice and lang are selected at call-time from the current reportLanguage:
   *   'EN'  → Google UK English Male, lang='en-GB'
   *   'FIL' → Filipino/Tagalog voice, lang='fil-PH'
   */
  const speak = useCallback((text, { priority } = {}) => {
    const voice = reportLanguage === 'FIL' ? filVoice.current : enVoice.current;
    if (!text || isMuted || !voice || !window.speechSynthesis) return;

    // ANTI-SPAM: skip identical text while still speaking it
    if (text === lastSpokenText.current && window.speechSynthesis.speaking) return;

    // CUTOFF: high-priority interrupts immediately
    if (priority === 'high') {
      window.speechSynthesis.cancel();
    }

    lastSpokenText.current = text;

    const utterance    = new SpeechSynthesisUtterance(text);
    utterance.voice    = voice;
    utterance.lang     = reportLanguage === 'FIL' ? 'fil-PH' : 'en-GB';
    utterance.pitch    = 0.9;
    utterance.rate     = 1.1;

    utterance.onstart = () => {
      clearTimeout(speakTimeout.current);
      setIsSpeaking(true);
    };

    utterance.onend = () => {
      speakTimeout.current = setTimeout(() => {
        if (!window.speechSynthesis.speaking) setIsSpeaking(false);
      }, 200);
    };

    utterance.onerror = () => {
      setIsSpeaking(false);
      lastSpokenText.current = '';
    };

    window.speechSynthesis.speak(utterance);
  }, [isMuted, reportLanguage]); // voice refs don't need deps — accessed via .current

  return { speak, isSpeaking, isMuted, toggleMute };
};
