import { useState, useEffect, useCallback, useRef } from 'react';

export const useJarvisVoice = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [jarvisVoice, setJarvisVoice] = useState(null);
  const speakTimeout = useRef(null);

  useEffect(() => {
    const loadVoices = () => {
      if (!window.speechSynthesis) return;
      const voices = window.speechSynthesis.getVoices();
      if (voices.length === 0) return;

      let selectedVoice =
        voices.find(v => v.name.includes('Google UK English Male')) ||
        voices.find(v => v.lang === 'en-GB' && v.name.toLowerCase().includes('male')) ||
        voices.find(v => v.lang === 'en-GB') ||
        voices[0];

      setJarvisVoice(selectedVoice);
    };

    loadVoices();
    if (window.speechSynthesis && window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }
  }, []);

  const toggleMute = useCallback(() => {
    setIsMuted(prev => {
      const nextMuteState = !prev;
      if (nextMuteState && window.speechSynthesis) {
        window.speechSynthesis.cancel();
        setIsSpeaking(false);
      }
      return nextMuteState;
    });
  }, []);

  const speak = useCallback((text) => {
    if (isMuted || !jarvisVoice || !window.speechSynthesis) return;

    // Notice we removed window.speechSynthesis.cancel() here 
    // so incoming rapid-fire process logs queue up naturally.

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = jarvisVoice;
    utterance.pitch = 0.9;
    utterance.rate = 1.1; // Slightly faster to keep up with the data stream

    utterance.onstart = () => {
      clearTimeout(speakTimeout.current);
      setIsSpeaking(true);
    };
    
    utterance.onend = () => {
      // Small buffer to prevent the visualizer from flickering between queued sentences
      speakTimeout.current = setTimeout(() => {
        if (!window.speechSynthesis.speaking) {
          setIsSpeaking(false);
        }
      }, 200);
    };
    
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  }, [isMuted, jarvisVoice]);

  return { speak, isSpeaking, isMuted, toggleMute };
};