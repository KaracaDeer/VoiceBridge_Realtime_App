import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Copy, Download, Volume2, VolumeX, Clock, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import './TranscriptionDisplay.css';

const TranscriptionDisplay = ({ transcriptions, isRecording }) => {
  const [selectedText, setSelectedText] = useState('');
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentTranscription, setCurrentTranscription] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  
  const messagesEndRef = useRef(null);
  const speechSynthesisRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [transcriptions]);

  useEffect(() => {
    // Simulate real-time typing effect for new transcriptions
    if (transcriptions.length > 0) {
      const latestTranscription = transcriptions[transcriptions.length - 1];
      if (latestTranscription.text !== currentTranscription) {
        setIsTyping(true);
        setCurrentTranscription(latestTranscription.text);
        
        if (typingTimeoutRef.current) {
          clearTimeout(typingTimeoutRef.current);
        }
        
        typingTimeoutRef.current = setTimeout(() => {
          setIsTyping(false);
        }, 1000);
      }
    }
  }, [transcriptions, currentTranscription]);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      toast.success('Text copied to clipboard');
    }).catch(() => {
      toast.error('Failed to copy text');
    });
  };

  const downloadTranscriptions = () => {
    const text = transcriptions.map(t => 
      `[${t.timestamp.toLocaleTimeString()}] ${t.text}`
    ).join('\n\n');
    
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `voicebridge-transcriptions-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast.success('Transcriptions downloaded');
  };

  const speakText = (text) => {
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    if (speechSynthesisRef.current) {
      window.speechSynthesis.cancel();
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    utterance.volume = 0.8;
    
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => {
      setIsSpeaking(false);
      toast.error('Speech synthesis failed');
    };

    speechSynthesisRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  };

  const formatTimestamp = (timestamp) => {
    return timestamp.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#22c55e';
    if (confidence >= 0.6) return '#f59e0b';
    return '#ef4444';
  };

  const getConfidenceText = (confidence) => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  return (
    <div className="transcription-display">
      <motion.div
        className="transcription-header"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="transcription-title">Live Transcription</h2>
        <p className="transcription-subtitle">Real-time speech-to-text results</p>
        
        <div className="transcription-actions">
          <motion.button
            className="action-button"
            onClick={downloadTranscriptions}
            disabled={transcriptions.length === 0}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title="Download all transcriptions"
          >
            <Download size={18} />
            <span>Download</span>
          </motion.button>
        </div>
      </motion.div>

      <div className="transcription-content">
        {/* Real-time typing indicator */}
        <AnimatePresence>
          {isRecording && (
            <motion.div
              className="typing-indicator"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="typing-dots">
                <motion.div
                  className="typing-dot"
                  animate={{ opacity: [0.4, 1, 0.4] }}
                  transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
                />
                <motion.div
                  className="typing-dot"
                  animate={{ opacity: [0.4, 1, 0.4] }}
                  transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
                />
                <motion.div
                  className="typing-dot"
                  animate={{ opacity: [0.4, 1, 0.4] }}
                  transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
                />
              </div>
              <span className="typing-text">Listening...</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Transcriptions List */}
        <div className="transcriptions-list">
          <AnimatePresence>
            {transcriptions.length === 0 ? (
              <motion.div
                className="empty-state"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
              >
                <div className="empty-icon">
                  <Volume2 size={48} />
                </div>
                <h3 className="empty-title">No transcriptions yet</h3>
                <p className="empty-subtitle">
                  Start recording or upload an audio file to see transcriptions here
                </p>
              </motion.div>
            ) : (
              transcriptions.map((transcription, index) => (
                <motion.div
                  key={transcription.id}
                  className="transcription-item"
                  initial={{ opacity: 0, y: 20, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -20, scale: 0.95 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  layout
                >
                  <div className="transcription-meta">
                    <div className="transcription-time">
                      <Clock size={14} />
                      <span>{formatTimestamp(transcription.timestamp)}</span>
                    </div>
                    <div 
                      className="transcription-confidence"
                      style={{ color: getConfidenceColor(transcription.confidence) }}
                    >
                      <CheckCircle size={14} />
                      <span>{getConfidenceText(transcription.confidence)}</span>
                    </div>
                  </div>
                  
                  <div className="transcription-text">
                    {transcription.text}
                  </div>
                  
                  <div className="transcription-actions">
                    <motion.button
                      className="transcription-action"
                      onClick={() => copyToClipboard(transcription.text)}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      title="Copy text"
                    >
                      <Copy size={16} />
                    </motion.button>
                    
                    <motion.button
                      className="transcription-action"
                      onClick={() => speakText(transcription.text)}
                      whileHover={{ scale: 1.1 }}
                      whileTap={{ scale: 0.9 }}
                      title={isSpeaking ? "Stop speaking" : "Speak text"}
                    >
                      {isSpeaking ? <VolumeX size={16} /> : <Volume2 size={16} />}
                    </motion.button>
                  </div>
                </motion.div>
              ))
            )}
          </AnimatePresence>
          
          <div ref={messagesEndRef} />
        </div>
      </div>
    </div>
  );
};

export default TranscriptionDisplay;
