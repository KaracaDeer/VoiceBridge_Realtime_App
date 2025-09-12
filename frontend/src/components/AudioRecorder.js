import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff, Square, Play, Pause, Upload } from 'lucide-react';
import { useWebSocket } from '../context/WebSocketContext';
import toast from 'react-hot-toast';
import './AudioRecorder.css';

const AudioRecorder = ({ isRecording, setIsRecording, onTranscription, setIsConnected }) => {
  const [isPaused, setIsPaused] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [audioLevel, setAudioLevel] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const streamRef = useRef(null);
  const timerRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const animationFrameRef = useRef(null);
  const fileInputRef = useRef(null);
  
  const { sendAudio, isConnected } = useWebSocket();

  useEffect(() => {
    setIsConnected(isConnected);
  }, [isConnected, setIsConnected]);

  useEffect(() => {
    if (isRecording && !isPaused) {
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [isRecording, isPaused]);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 16000,
          channelCount: 1
        } 
      });
      
      streamRef.current = stream;
      
      // Set up audio analysis for level visualization
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 256;
      source.connect(analyserRef.current);
      
      // Start audio level monitoring
      monitorAudioLevel();
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        setAudioBlob(audioBlob);
        setAudioUrl(URL.createObjectURL(audioBlob));
        processAudio(audioBlob);
      };
      
      mediaRecorder.start(100); // Collect data every 100ms for real-time streaming
      setIsRecording(true);
      setRecordingTime(0);
      
      toast.success('Recording started');
      
    } catch (error) {
      console.error('Error starting recording:', error);
      toast.error('Failed to start recording. Please check microphone permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      setIsPaused(false);
      setRecordingTime(0);
      
      // Stop audio level monitoring
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      
      // Clean up audio context
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
      
      // Stop media stream
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      
      toast.success('Recording stopped');
    }
  };

  const pauseRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      if (isPaused) {
        mediaRecorderRef.current.resume();
        setIsPaused(false);
        toast.success('Recording resumed');
      } else {
        mediaRecorderRef.current.pause();
        setIsPaused(true);
        toast.success('Recording paused');
      }
    }
  };

  const monitorAudioLevel = () => {
    if (!analyserRef.current) return;
    
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    
    const updateLevel = () => {
      if (!isRecording || isPaused) {
        setAudioLevel(0);
        return;
      }
      
      analyserRef.current.getByteFrequencyData(dataArray);
      const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
      setAudioLevel(average / 255);
      
      animationFrameRef.current = requestAnimationFrame(updateLevel);
    };
    
    updateLevel();
  };

  const processAudio = async (audioBlob) => {
    setIsProcessing(true);
    
    try {
      // Convert blob to array buffer for WebSocket
      const arrayBuffer = await audioBlob.arrayBuffer();
      
      // Send audio data via WebSocket for real-time processing
      const success = sendAudio(arrayBuffer);
      
      if (success) {
        toast.success('Audio sent for processing');
      } else {
        toast.error('Failed to send audio data');
      }
      
    } catch (error) {
      console.error('Error processing audio:', error);
      toast.error('Error processing audio');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type.startsWith('audio/')) {
        setAudioBlob(file);
        setAudioUrl(URL.createObjectURL(file));
        processAudio(file);
        toast.success('Audio file uploaded');
      } else {
        toast.error('Please select an audio file');
      }
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="audio-recorder">
      <motion.div
        className="recorder-header"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <h2 className="recorder-title">Audio Recorder</h2>
        <p className="recorder-subtitle">Record or upload audio for real-time transcription</p>
      </motion.div>

      <div className="recorder-content">
        {/* Recording Controls */}
        <motion.div
          className="recording-controls"
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
        >
          <motion.button
            className={`record-button ${isRecording ? 'recording' : ''}`}
            onClick={isRecording ? stopRecording : startRecording}
            disabled={isProcessing}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            animate={{
              scale: isRecording ? [1, 1.1, 1] : 1,
            }}
            transition={{
              duration: 1,
              repeat: isRecording ? Infinity : 0,
              ease: "easeInOut"
            }}
          >
            <AnimatePresence mode="wait">
              {isRecording ? (
                <motion.div
                  key="stop"
                  initial={{ scale: 0, rotate: -90 }}
                  animate={{ scale: 1, rotate: 0 }}
                  exit={{ scale: 0, rotate: 90 }}
                  transition={{ duration: 0.2 }}
                >
                  <Square size={24} />
                </motion.div>
              ) : (
                <motion.div
                  key="record"
                  initial={{ scale: 0, rotate: 90 }}
                  animate={{ scale: 1, rotate: 0 }}
                  exit={{ scale: 0, rotate: -90 }}
                  transition={{ duration: 0.2 }}
                >
                  <Mic size={24} />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.button>

          {isRecording && (
            <motion.button
              className="pause-button"
              onClick={pauseRecording}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0, opacity: 0 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {isPaused ? <Play size={20} /> : <Pause size={20} />}
            </motion.button>
          )}

          <motion.button
            className="upload-button"
            onClick={() => fileInputRef.current?.click()}
            disabled={isRecording || isProcessing}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            <Upload size={20} />
            <span>Upload</span>
          </motion.button>
        </motion.div>

        {/* Recording Status */}
        <AnimatePresence>
          {isRecording && (
            <motion.div
              className="recording-status"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <div className="recording-info">
                <div className="recording-time">
                  {formatTime(recordingTime)}
                </div>
                <div className="recording-state">
                  {isPaused ? 'Paused' : 'Recording...'}
                </div>
              </div>
              
              <div className="audio-level-indicator">
                <div className="level-bars">
                  {Array.from({ length: 20 }, (_, i) => (
                    <motion.div
                      key={i}
                      className="level-bar"
                      animate={{
                        height: audioLevel > (i / 20) ? '100%' : '20%',
                        backgroundColor: audioLevel > (i / 20) ? 
                          `hsl(${120 + (i * 2)}, 70%, 50%)` : 
                          'rgba(255, 255, 255, 0.3)'
                      }}
                      transition={{ duration: 0.1 }}
                    />
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Processing Status */}
        <AnimatePresence>
          {isProcessing && (
            <motion.div
              className="processing-status"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <div className="processing-spinner" />
              <span>Processing audio...</span>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Audio Preview */}
        <AnimatePresence>
          {audioUrl && (
            <motion.div
              className="audio-preview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <audio controls src={audioUrl} className="audio-player" />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="audio/*"
        onChange={handleFileUpload}
        style={{ display: 'none' }}
      />
    </div>
  );
};

export default AudioRecorder;
