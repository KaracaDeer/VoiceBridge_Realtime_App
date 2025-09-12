/**
 * VoiceBridge Frontend Application
 * 
 * This is the main React component that provides the user interface for
 * real-time speech-to-text functionality. It includes:
 * - WebSocket connection for real-time audio streaming
 * - Browser-based speech recognition as fallback
 * - Audio recording and processing
 * - Transcription display and management
 * - Responsive design for mobile and desktop
 */

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster, toast } from 'react-hot-toast';
import { ArrowLeft } from 'lucide-react';
import { useWebSocket, WebSocketProvider } from './context/WebSocketContext';
import WebSpeechService from './services/webSpeechService';
import './App.css';


const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.6,
      when: "beforeChildren",
      staggerChildren: 0.1
    }
  },
};


// Audio Waveform Component - Visual representation of audio input levels
const AudioWaveform = ({ audioLevel, isRecording }) => {
  const bars = Array.from({ length: 20 }, (_, i) => {
    const baseHeight = 4;
    const maxHeight = 40;
    const randomMultiplier = Math.random() * 0.5 + 0.5; // 0.5 to 1
    const height = isRecording 
      ? baseHeight + (audioLevel * maxHeight * randomMultiplier)
      : baseHeight;
    
    return (
      <motion.div
        key={i}
        className="waveform-bar"
        animate={{
          height: height,
          opacity: isRecording ? 0.8 + (audioLevel * 0.4) : 0.4
        }}
        transition={{
          duration: 0.1,
          ease: "easeOut"
        }}
      />
    );
  });

  return (
    <div className="audio-waveform">
      {bars}
    </div>
  );
};

function AppContent() {
  // WebSocket connection for real-time audio streaming to backend
  const { sendAudio, lastMessage, isConnected, connect } = useWebSocket();
  
  // Recording state management
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [transcriptions, setTranscriptions] = useState([]);
  const [timerInterval, setTimerInterval] = useState(null);
  
  // Audio processing and visualization
  const [audioLevel, setAudioLevel] = useState(0);
  const [audioContext, setAudioContext] = useState(null);
  
  // UI state management
  const [currentPage, setCurrentPage] = useState('welcome'); // 'welcome' or 'recording'
  const [currentTranscription, setCurrentTranscription] = useState('');
  const [webSpeechService, setWebSpeechService] = useState(null);
  const [useWebSpeech, setUseWebSpeech] = useState(true); // Use Web Speech API by default
  const [messagesEndRef, setMessagesEndRef] = useState(null);

  // Initialize Web Speech Service as fallback when WebSocket is not available
  useEffect(() => {
    if (WebSpeechService.isSupported()) {
      const speechService = new WebSpeechService();
      
      // Set up event handlers
      speechService.setOnResult((result) => {
        if (result.isFinal) {
          // Add final transcription to list
          const capitalizedText = result.text.charAt(0).toUpperCase() + result.text.slice(1);
          const newTranscription = {
            id: Date.now() + Math.random(),
            text: capitalizedText,
            timestamp: new Date(result.timestamp),
            confidence: result.confidence,
            provider: result.provider,
            isManual: false
          };
          
          setTranscriptions(prev => [...prev, newTranscription]);
          // Don't clear current transcription - keep it visible until new recording starts
        } else {
          // Update current transcription with interim results
          const capitalizedText = result.text.charAt(0).toUpperCase() + result.text.slice(1);
          setCurrentTranscription(capitalizedText);
        }
      });

      speechService.setOnError((error) => {
        console.error('Web Speech Error:', error);
        // toast.error(error.message);
        setIsRecording(false);
      });

      speechService.setOnStart(() => {
        console.log('Web Speech started');
        setIsRecording(true);
      });

      speechService.setOnEnd(() => {
        console.log('Web Speech ended');
        setIsRecording(false);
      });

      setWebSpeechService(speechService);
      
      const browserInfo = WebSpeechService.getBrowserInfo();
      console.log('🎤 Web Speech API:', browserInfo);
      // toast.success('Web Speech API ready! (Free browser-based recognition)');
    } else {
      console.warn('Web Speech API not supported');
      toast.error('Web Speech API not supported in this browser');
      setUseWebSpeech(false);
    }

    // Auto-connect to WebSocket as fallback
    connect();
  }, [connect]); // Include connect in dependencies

  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (messagesEndRef) {
      messagesEndRef.scrollIntoView({ behavior: 'smooth' });
    }
  }, [transcriptions, currentTranscription, messagesEndRef]);

  useEffect(() => {
    if (lastMessage) {
      try {
        const data = JSON.parse(lastMessage);
        if (data.type === 'transcription' && data.text) {
          // Update current transcription
          setCurrentTranscription(data.text);
          
          // Add to transcriptions list
          const newTranscription = {
            id: Date.now() + Math.random(),
            text: data.text,
            timestamp: new Date(data.timestamp * 1000 || Date.now()), // Convert from Unix timestamp if provided
            confidence: data.confidence || 0.95,
            isManual: false
          };
          
          setTranscriptions(prev => [...prev, newTranscription]);
          
          // Don't clear current transcription - keep it visible until new recording starts
          
          // Show success toast
          toast.success('Speech recognized!');
        } else if (data.type === 'error') {
          console.log(`Backend Error: ${data.message}`);
          toast.error(`Transcription error: ${data.message}`);
        }
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e, lastMessage);
      }
    }
  }, [lastMessage]);

  useEffect(() => {
    if (isRecording) {
      // Clear any existing interval first
      if (timerInterval) {
        clearInterval(timerInterval);
      }
      
      const newInterval = setInterval(() => {
        // Timer logic can be added here if needed
      }, 1000);
      setTimerInterval(newInterval);
    } else {
      if (timerInterval) {
        clearInterval(timerInterval);
        setTimerInterval(null);
      }
      // Reset timer if needed
    }
    
    // Cleanup function
    return () => {
      if (timerInterval) {
        clearInterval(timerInterval);
      }
    };
  }, [isRecording, timerInterval]); // Include timerInterval in dependencies

  const startRecording = async () => {
    // Switch to recording page
    setCurrentPage('recording');
    // Clear current transcription when starting new recording
    setCurrentTranscription('');
    
    if (useWebSpeech && webSpeechService) {
      // Use Web Speech API (free, browser-based)
      try {
        const started = webSpeechService.start();
        if (started) {
          // toast.success('🎤 Web Speech Recognition started (Free!)');
          return;
        } else {
          // toast.error('Failed to start Web Speech Recognition');
          setCurrentPage('welcome');
          return;
        }
      } catch (error) {
        console.error("Web Speech error:", error);
        toast.error("Web Speech Recognition failed. Trying fallback...");
        // Fall back to WebSocket method
      }
    }

    // Fallback to WebSocket method (requires OpenAI API)
    if (!isConnected) {
      connect();
      // Wait a bit for connection to establish
      await new Promise(resolve => setTimeout(resolve, 500));
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setMicrophoneStream(stream);
      // Configure MediaRecorder with proper format for speech recognition
      let options = {};
      
      // WAV is best for speech recognition, but not supported by all browsers
      if (MediaRecorder.isTypeSupported('audio/wav')) {
        options = { mimeType: 'audio/wav' };
      } else if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        options = { mimeType: 'audio/webm;codecs=opus' };
      } else if (MediaRecorder.isTypeSupported('audio/webm')) {
        options = { mimeType: 'audio/webm' };
      }
      
      const newMediaRecorder = new MediaRecorder(stream, options);
      console.log('MediaRecorder format:', newMediaRecorder.mimeType);
      setMediaRecorder(newMediaRecorder);

      const newAudioContext = new (window.AudioContext || window.webkitAudioContext)();
      const source = newAudioContext.createMediaStreamSource(stream);
      const newAnalyser = newAudioContext.createAnalyser();
      newAnalyser.fftSize = 256;
      source.connect(newAnalyser);
      setAudioContext(newAudioContext);
      setAnalyser(newAnalyser);

      const dataArray = new Uint8Array(newAnalyser.frequencyBinCount);
      const updateAudioLevel = () => {
        newAnalyser.getByteFrequencyData(dataArray);
        const sum = dataArray.reduce((a, b) => a + b, 0);
        const average = sum / dataArray.length;
        setAudioLevel(average / 256);
        if (isRecording) {
          requestAnimationFrame(updateAudioLevel);
        }
      };
      requestAnimationFrame(updateAudioLevel);

      newMediaRecorder.ondataavailable = async (event) => {
        if (event.data.size > 0) {
          console.log(`Recording chunk: ${event.data.size} bytes, type: ${event.data.type}`);
          
          // For now, skip WAV conversion due to encoding issues with chunks
          // Send WebM directly - backend will handle format detection
          sendAudio(event.data);
        }
      };

      newMediaRecorder.onstop = () => {
        stream.getTracks().forEach(track => track.stop());
        if (audioContext) audioContext.close();
        setAudioLevel(0);
        setMicrophoneStream(null);
      };

      newMediaRecorder.start(2000); // Send data every 2 seconds
      setIsRecording(true);
      // toast.success('🎤 Recording started (WebSocket fallback)');
    } catch (error) {
      console.error("Error starting recording:", error);
      toast.error("Failed to start recording. Please check microphone permissions.");
      setIsRecording(false);
      setCurrentPage('welcome'); // Go back to welcome page on error
    }
  };

  const stopRecording = () => {
    if (useWebSpeech && webSpeechService && isRecording) {
      // Stop Web Speech API
      webSpeechService.stop();
      // toast.success('🛑 Web Speech Recognition stopped');
      return;
    }
    
    // Stop WebSocket recording
    if (mediaRecorder && isRecording) {
      mediaRecorder.stop();
      setIsRecording(false);
      // toast.success('🛑 Recording stopped');
    }
    
    // Don't clear currentTranscription when stopping - keep it visible
    // It will only be cleared when starting a new recording
  };

  const handleCloseChat = () => {
    setIsRecording(false);
    
    // Stop Web Speech if active
    if (webSpeechService && isRecording) {
      webSpeechService.stop();
    }
    
    // Stop MediaRecorder if active
    if (mediaRecorder) {
      mediaRecorder.stop();
    }
  };

  const handleClearTranscriptions = () => {
    // Clear all transcriptions and current transcription
    setTranscriptions([]);
    setCurrentTranscription('');
  };

  return (
    <div className="App">
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 3000,
          style: {
            background: 'rgba(255, 255, 255, 0.15)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            color: 'white',
            borderRadius: '16px',
          },
        }}
      />

      <AnimatePresence mode="wait">
        {currentPage === 'welcome' ? (
          <motion.div
            key="welcome"
            className="app-container"
            variants={containerVariants}
            initial="hidden"
            animate="visible"
            exit="hidden"
          >
            <motion.div
              className="main-app-content"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.5 }}
            >
              {/* Logo Header */}
              <motion.div
                className="logo-header"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1, duration: 0.6 }}
              >
                <h1 className="app-logo">VoiceBridge</h1>
                <motion.div 
                  className="logo-subtitle"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3, duration: 0.8 }}
                >
                  <span className="subtitle-text">Voice to Text • Instantly</span>
                  <div className="subtitle-decorations">
                    <span className="decoration-dot"></span>
                    <span className="decoration-line"></span>
                    <span className="decoration-dot"></span>
                  </div>
                </motion.div>
              </motion.div>

              {/* Clear Button - Hidden on welcome page */}
              {/* {transcriptions.length > 0 && (
                <motion.button
                  className="clear-button"
                  onClick={handleCloseChat}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.2 }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <X size={16} /> Clear All
                </motion.button>
              )} */}

              {/* Main Content */}
              <div className="main-content-area">
                {/* Central Bubble */}
                <motion.div
                  className="bubble-container"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.4, duration: 0.6 }}
                >
                  <motion.div
                    className={`speech-bubble ${isRecording ? 'recording' : ''}`}
                    onClick={isRecording ? stopRecording : startRecording}
                    animate={isRecording ? {
                      scale: [1, 1.15, 1],
                      rotate: [0, 5, -5, 0],
                      y: [0, -8, 0],
                      filter: ["brightness(1)", "brightness(1.2)", "brightness(1)"]
                    } : {
                      scale: [1, 1.06, 1],
                      y: [0, -6, 0],
                      rotate: [0, 3, -3, 0]
                    }}
                    transition={isRecording ? {
                      scale: { duration: 1.5, repeat: Infinity, ease: "easeInOut" },
                      rotate: { duration: 2, repeat: Infinity, ease: "easeInOut" },
                      y: { duration: 1.8, repeat: Infinity, ease: "easeInOut" },
                      filter: { duration: 1.5, repeat: Infinity, ease: "easeInOut" }
                    } : {
                      scale: { duration: 3, repeat: Infinity, ease: "easeInOut" },
                      y: { duration: 3.5, repeat: Infinity, ease: "easeInOut" },
                      rotate: { duration: 4, repeat: Infinity, ease: "easeInOut" }
                    }}
                    whileHover={{ 
                      scale: 1.06,
                      y: -2,
                      transition: { duration: 0.3, ease: "easeOut" }
                    }}
                    whileTap={{ 
                      scale: 0.96,
                      transition: { duration: 0.1, ease: "easeOut" }
                    }}
                  >
                    <div className="bubble-gradient"></div>
                    <motion.div 
                      className="bubble-glow"
                      animate={isRecording ? {
                        opacity: [0.4, 0.8, 0.4],
                        scale: [1, 1.4, 1]
                      } : {
                        opacity: [0.2, 0.5, 0.2],
                        scale: [1, 1.2, 1]
                      }}
                      transition={{
                        duration: isRecording ? 1.5 : 3,
                        repeat: Infinity,
                        ease: "easeInOut"
                      }}
                    />
                  </motion.div>
                </motion.div>

                {/* Speech Text */}
                <motion.div
                  className="speech-text"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                >
                  <h2>{isRecording ? "Listening to your voice..." : "Welcome to VoiceBridge"}</h2>
                  <p>{isRecording ? "Recording in progress" : "Ready to transcribe your speech"}</p>
                </motion.div>

                {/* Transcriptions - Hidden on welcome page */}
                {/* {transcriptions.length > 0 && (
                  <motion.div
                    className="transcriptions-container"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.8, duration: 0.6 }}
                  >
                    <AnimatePresence>
                      {transcriptions.map((t) => (
                        <motion.div
                          key={t.id}
                          className={`transcription-item ${t.isManual ? 'manual' : ''}`}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          exit={{ opacity: 0, x: -20 }}
                          layout
                        >
                          <div className="transcription-meta">
                            <span className="transcription-time">
                              {new Date(t.timestamp).toLocaleTimeString()}
                            </span>
                            {t.confidence > 0 && (
                              <span className="transcription-confidence">
                                Confidence: {(t.confidence * 100).toFixed(0)}%
                              </span>
                            )}
                            {t.provider && (
                              <span className="transcription-provider">
                                {t.provider === 'web_speech_api' ? '🆓 Web Speech' : '🤖 OpenAI'}
                              </span>
                            )}
                          </div>
                          <p className="transcription-text">{t.text}</p>
                          <div className="transcription-actions">
                            <motion.button
                              className="transcription-action"
                              onClick={() => navigator.clipboard.writeText(t.text)}
                              whileHover={{ scale: 1.1 }}
                              whileTap={{ scale: 0.9 }}
                            >
                              <Copy size={16} />
                            </motion.button>
                            <motion.button
                              className="transcription-action"
                              onClick={() => {
                                const utterance = new SpeechSynthesisUtterance(t.text);
                                window.speechSynthesis.speak(utterance);
                              }}
                              whileHover={{ scale: 1.1 }}
                              whileTap={{ scale: 0.9 }}
                            >
                              <Volume2 size={16} />
                            </motion.button>
                          </div>
                        </motion.div>
                      ))}
                    </AnimatePresence>
                  </motion.div>
                )} */}
              </div>

              {/* Bottom Instructions */}
              <motion.div 
                className="bottom-instructions"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.2, duration: 0.6 }}
              >
                <p>{isRecording ? "Recording in progress..." : "Tap the voice button to start speaking"}</p>
                <motion.div 
                  className="status-indicators"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 1.4 }}
                >
                  <div className="status-dots">
                    <span className={`status-dot ${isRecording ? 'active' : ''}`}></span>
                    <span className={`status-dot ${isRecording ? 'active' : ''}`}></span>
                    <span className={`status-dot ${isRecording ? 'active' : ''}`}></span>
                  </div>
                </motion.div>
              </motion.div>
            </motion.div>
          </motion.div>
        ) : (
          // Recording Page - Text Interface
          <motion.div
            key="recording"
            className="app-container recording-page"
            initial={{ opacity: 0, x: 100 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -100 }}
            transition={{ duration: 0.5 }}
          >
            <motion.div
              className="main-app-content"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2, duration: 0.5 }}
            >
              {/* Logo Header - Same as welcome page */}
              <motion.div
                className="logo-header"
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1, duration: 0.6 }}
              >
                <h1 className="app-logo">VoiceBridge</h1>
                <motion.div 
                  className="logo-subtitle"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.3, duration: 0.8 }}
                >
                  <span className="subtitle-text">Voice to Text • Instantly</span>
                  <div className="subtitle-decorations">
                    <span className="decoration-dot"></span>
                    <span className="decoration-line"></span>
                    <span className="decoration-dot"></span>
                  </div>
                </motion.div>
              </motion.div>

              {/* Back Button */}
              <motion.button
                className="back-button"
                onClick={() => setCurrentPage('welcome')}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <ArrowLeft size={20} />
              </motion.button>

              {/* Text Content Area */}
              <motion.div
                className="text-content-area"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <motion.div
                  className="text-display"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.6 }}
                >
                  {/* All Transcriptions as Continuous Text */}
                  {transcriptions.length > 0 && (
                    <motion.div
                      className="transcription-text-content"
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3 }}
                    >
                      {transcriptions.map((transcription, index) => (
                        <motion.span
                          key={transcription.id}
                          className="transcription-sentence"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ 
                            duration: 0.3,
                            delay: index * 0.1 
                          }}
                        >
                          {transcription.text}
                          {index < transcriptions.length - 1 && ' '}
                        </motion.span>
                      ))}
                    </motion.div>
                  )}
                  
                  {/* Current/Interim Transcription */}
                  {currentTranscription && (
                    <motion.span
                      className="interim-transcription-text"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.3 }}
                    >
                      {currentTranscription}
                    </motion.span>
                  )}

                  {/* Empty State */}
                  {transcriptions.length === 0 && !currentTranscription && (
                    <motion.div
                      className="empty-text-state"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.6 }}
                    >
                      <p>Your transcribed text will appear here as you speak...</p>
                    </motion.div>
                  )}
                </motion.div>
                
                {/* Auto-scroll target */}
                <div ref={setMessagesEndRef} />
              </motion.div>

              {/* Bottom Control Area */}
              <motion.div
                className="recording-controls"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
              >
                {/* Audio Waveform */}
                {isRecording && (
                  <motion.div
                    className="waveform-container compact"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <AudioWaveform audioLevel={audioLevel} isRecording={isRecording} />
                  </motion.div>
                )}

                {/* Buttons Container */}
                <div className="buttons-container">
                  {/* Recording Button */}
                  <motion.div
                    className="record-button-container"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <motion.button
                      className={`record-button ${isRecording ? 'recording' : ''}`}
                      onClick={isRecording ? stopRecording : startRecording}
                      animate={isRecording ? {
                        scale: [1, 1.05, 1],
                        boxShadow: [
                          "0 0 0 0 rgba(156, 163, 219, 0.7)",
                          "0 0 0 10px rgba(156, 163, 219, 0)",
                          "0 0 0 0 rgba(156, 163, 219, 0.7)"
                        ]
                      } : {}}
                      transition={isRecording ? {
                        duration: 1.5,
                        repeat: Infinity,
                        ease: "easeInOut"
                      } : {}}
                    >
                      <div className="record-button-inner">
                        {isRecording ? (
                          <motion.div
                            className="stop-icon"
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ duration: 0.2 }}
                          />
                        ) : (
                          <motion.div
                            className="record-icon"
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ duration: 0.2 }}
                          >
                            ●
                          </motion.div>
                        )}
                      </div>
                    </motion.button>
                    
                    <p className="record-button-label">
                      {isRecording ? "Tap to stop" : "Tap to record"}
                    </p>
                  </motion.div>

                  {/* Clear Button */}
                  <motion.div
                    className="clear-button-container"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <motion.button
                      className="clear-button"
                      onClick={handleClearTranscriptions}
                      disabled={transcriptions.length === 0 && !currentTranscription}
                    >
                      <div className="clear-button-inner">
                        <motion.div
                          className="clear-icon"
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          transition={{ duration: 0.2 }}
                        >
                          🗑️
                        </motion.div>
                      </div>
                    </motion.button>
                    
                    <p className="clear-button-label">
                      Clear
                    </p>
                  </motion.div>
                </div>
              </motion.div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Background Animation - Removed for clean white background */}
    </div>
  );
}

function App() {
  return (
    <WebSocketProvider>
      <AppContent />
    </WebSocketProvider>
  );
}

export default App;