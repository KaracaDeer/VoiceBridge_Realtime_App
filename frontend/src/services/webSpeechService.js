/**
 * Web Speech API Service
 * Browser-based speech recognition (free!)
 */

class WebSpeechService {
  constructor() {
    this.recognition = null;
    this.isListening = false;
    this.onResult = null;
    this.onError = null;
    this.onStart = null;
    this.onEnd = null;
    this.language = 'en-US'; // Default to English
    
    this.initRecognition();
  }

  initRecognition() {
    // Check browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      console.error('Speech Recognition API not supported in this browser');
      return false;
    }

    this.recognition = new SpeechRecognition();
    
    // Configure recognition settings
    this.recognition.continuous = true; // Keep listening
    this.recognition.interimResults = true; // Get partial results
    this.recognition.lang = this.language;
    this.recognition.maxAlternatives = 1;

    // Event handlers
    this.recognition.onstart = () => {
      console.log('🎤 Web Speech Recognition started');
      this.isListening = true;
      if (this.onStart) this.onStart();
    };

    this.recognition.onend = () => {
      console.log('🛑 Web Speech Recognition ended');
      this.isListening = false;
      if (this.onEnd) this.onEnd();
    };

    this.recognition.onresult = (event) => {
      let finalTranscript = '';
      let interimTranscript = '';

      // Process all results
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        const confidence = event.results[i][0].confidence || 0.9;

        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
          console.log('✅ Final transcript:', transcript, `(confidence: ${confidence.toFixed(2)})`);
          
          if (this.onResult) {
            this.onResult({
              text: transcript.trim(),
              confidence: confidence,
              isFinal: true,
              timestamp: Date.now(),
              provider: 'web_speech_api'
            });
          }
        } else {
          interimTranscript += transcript;
          console.log('⏳ Interim transcript:', transcript);
          
          if (this.onResult) {
            this.onResult({
              text: transcript.trim(),
              confidence: confidence,
              isFinal: false,
              timestamp: Date.now(),
              provider: 'web_speech_api'
            });
          }
        }
      }
    };

    this.recognition.onerror = (event) => {
      console.error('🚨 Speech Recognition Error:', event.error);
      
      let errorMessage = 'Speech recognition error';
      switch (event.error) {
        case 'no-speech':
          errorMessage = 'No speech detected. Please try speaking again.';
          break;
        case 'audio-capture':
          errorMessage = 'Audio capture failed. Check your microphone.';
          break;
        case 'not-allowed':
          errorMessage = 'Microphone permission denied. Please allow microphone access.';
          break;
        case 'network':
          errorMessage = 'Network error occurred during speech recognition.';
          break;
        case 'aborted':
          errorMessage = 'Speech recognition was aborted.';
          break;
        default:
          errorMessage = `Speech recognition error: ${event.error}`;
      }

      if (this.onError) {
        this.onError({
          error: event.error,
          message: errorMessage,
          timestamp: Date.now()
        });
      }
    };

    return true;
  }

  // Start listening
  start() {
    if (!this.recognition) {
      console.error('Speech Recognition not initialized');
      return false;
    }

    if (this.isListening) {
      console.log('Already listening...');
      return true;
    }

    try {
      this.recognition.start();
      return true;
    } catch (error) {
      console.error('Error starting speech recognition:', error);
      return false;
    }
  }

  // Stop listening
  stop() {
    if (!this.recognition || !this.isListening) {
      return;
    }

    try {
      this.recognition.stop();
    } catch (error) {
      console.error('Error stopping speech recognition:', error);
    }
  }

  // Abort recognition
  abort() {
    if (!this.recognition) {
      return;
    }

    try {
      this.recognition.abort();
      this.isListening = false;
    } catch (error) {
      console.error('Error aborting speech recognition:', error);
    }
  }

  // Set language
  setLanguage(language) {
    this.language = language;
    if (this.recognition) {
      this.recognition.lang = language;
    }
  }

  // Set event handlers
  setOnResult(callback) {
    this.onResult = callback;
  }

  setOnError(callback) {
    this.onError = callback;
  }

  setOnStart(callback) {
    this.onStart = callback;
  }

  setOnEnd(callback) {
    this.onEnd = callback;
  }

  // Check if browser supports speech recognition
  static isSupported() {
    return !!(window.SpeechRecognition || window.webkitSpeechRecognition);
  }

  // Get browser compatibility info
  static getBrowserInfo() {
    const isSupported = WebSpeechService.isSupported();
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    return {
      isSupported,
      api: SpeechRecognition ? 'Available' : 'Not Available',
      browser: navigator.userAgent.includes('Chrome') ? 'Chrome' : 
               navigator.userAgent.includes('Edge') ? 'Edge' : 
               navigator.userAgent.includes('Safari') ? 'Safari' : 
               'Other',
      vendor: window.webkitSpeechRecognition ? 'WebKit' : 'Standard'
    };
  }

  // Get supported languages (common ones)
  static getSupportedLanguages() {
    return [
      { code: 'en-US', name: 'English (US)' },
      { code: 'en-GB', name: 'English (UK)' },
      { code: 'tr-TR', name: 'Turkish' },
      { code: 'es-ES', name: 'Spanish' },
      { code: 'fr-FR', name: 'French' },
      { code: 'de-DE', name: 'German' },
      { code: 'it-IT', name: 'Italian' },
      { code: 'pt-PT', name: 'Portuguese' },
      { code: 'ru-RU', name: 'Russian' },
      { code: 'ja-JP', name: 'Japanese' },
      { code: 'ko-KR', name: 'Korean' },
      { code: 'zh-CN', name: 'Chinese (Simplified)' },
      { code: 'ar-SA', name: 'Arabic' },
      { code: 'hi-IN', name: 'Hindi' },
      { code: 'nl-NL', name: 'Dutch' },
      { code: 'sv-SE', name: 'Swedish' }
    ];
  }
}

export default WebSpeechService;
