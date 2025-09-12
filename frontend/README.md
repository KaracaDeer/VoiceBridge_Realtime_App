# VoiceBridge Frontend

Modern, responsive React.js frontend for the VoiceBridge real-time speech-to-text application.

## Features

- **Real-time Audio Recording**: WebRTC-based audio capture with visual feedback
- **Live Transcription Display**: Real-time speech-to-text results with confidence indicators
- **WebSocket Integration**: Seamless real-time communication with backend
- **Modern UI/UX**: Beautiful, accessible interface with Framer Motion animations
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Audio Playback**: Built-in audio player for recorded content
- **Export Functionality**: Download transcriptions as text files
- **Text-to-Speech**: Built-in speech synthesis for accessibility

## Technology Stack

- **React 18**: Modern React with hooks and functional components
- **Framer Motion**: Smooth animations and transitions
- **Lucide React**: Beautiful, consistent icons
- **React Hot Toast**: Elegant notification system
- **WebSocket API**: Real-time communication
- **WebRTC MediaRecorder**: Audio recording capabilities
- **CSS3**: Modern styling with backdrop filters and gradients

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- VoiceBridge backend running on localhost:8000

### Installation

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm start
   ```

3. **Open in browser**
   ```
   http://localhost:3000
   ```

### Environment Configuration

Create a `.env` file in the frontend directory:

```env
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_API_URL=http://localhost:8000
REACT_APP_APP_NAME=VoiceBridge
REACT_APP_VERSION=1.0.0
REACT_APP_DEBUG=true
```

## Usage

### Recording Audio

1. **Click the microphone button** to start recording
2. **Speak clearly** into your microphone
3. **Watch the audio level indicator** for visual feedback
4. **Click the stop button** to end recording
5. **View transcription results** in real-time

### Uploading Audio Files

1. **Click the upload button**
2. **Select an audio file** (WAV, MP3, M4A, FLAC)
3. **Wait for processing** to complete
4. **View transcription results**

### Managing Transcriptions

- **Copy text** to clipboard using the copy button
- **Listen to text** using the speaker button
- **Download all transcriptions** as a text file
- **Clear all transcriptions** using the clear button

## Component Architecture

```
src/
├── components/
│   ├── Header.js              # App header with logo and controls
│   ├── AudioRecorder.js       # Audio recording interface
│   ├── TranscriptionDisplay.js # Live transcription results
│   └── ConnectionStatus.js    # WebSocket connection indicator
├── context/
│   └── WebSocketContext.js    # WebSocket connection management
├── App.js                     # Main application component
├── App.css                    # Global application styles
├── index.js                   # Application entry point
└── index.css                  # Global styles and resets
```

## Key Features

### Real-time Audio Processing

- **WebRTC MediaRecorder**: High-quality audio capture
- **Audio Level Visualization**: Real-time audio level feedback
- **Chunked Streaming**: Efficient real-time data transmission
- **Noise Suppression**: Built-in audio enhancement

### WebSocket Communication

- **Automatic Reconnection**: Handles connection drops gracefully
- **Message Queuing**: Ensures reliable data transmission
- **Error Handling**: Comprehensive error management
- **Status Indicators**: Visual connection status feedback

### Accessibility Features

- **Keyboard Navigation**: Full keyboard accessibility
- **Screen Reader Support**: ARIA labels and semantic HTML
- **High Contrast Mode**: Support for high contrast displays
- **Reduced Motion**: Respects user motion preferences
- **Text-to-Speech**: Built-in speech synthesis

### Responsive Design

- **Mobile-First**: Optimized for mobile devices
- **Flexible Layout**: Adapts to any screen size
- **Touch-Friendly**: Large touch targets for mobile
- **Progressive Enhancement**: Works without JavaScript

## Customization

### Styling

The application uses CSS custom properties for easy theming:

```css
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  --success-color: #22c55e;
  --error-color: #ef4444;
  --warning-color: #f59e0b;
}
```

### Animation Configuration

Framer Motion animations can be customized in component files:

```javascript
const animationVariants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 }
};
```

## Performance Optimization

- **Code Splitting**: Automatic code splitting with React.lazy
- **Memoization**: React.memo for expensive components
- **Debounced Inputs**: Optimized user input handling
- **Efficient Re-renders**: Minimized unnecessary re-renders
- **Lazy Loading**: Components loaded on demand

## Browser Support

- **Chrome 80+**: Full support
- **Firefox 75+**: Full support
- **Safari 13+**: Full support
- **Edge 80+**: Full support
- **Mobile Browsers**: iOS Safari 13+, Chrome Mobile 80+

## Development

### Available Scripts

```bash
npm start          # Start development server
npm run build      # Build for production
npm test           # Run tests
npm run eject      # Eject from Create React App
```

### Code Style

- **ESLint**: Configured for React best practices
- **Prettier**: Automatic code formatting
- **Functional Components**: Modern React patterns
- **Hooks**: Custom hooks for reusable logic

## Deployment

### Production Build

```bash
npm run build
```

### Environment Variables

Set production environment variables:

```env
REACT_APP_WS_URL=wss://your-domain.com
REACT_APP_API_URL=https://your-domain.com
REACT_APP_DEBUG=false
```

### Static Hosting

The build folder can be deployed to any static hosting service:

- **Netlify**: Drag and drop deployment
- **Vercel**: Git-based deployment
- **AWS S3**: Static website hosting
- **GitHub Pages**: Free hosting for public repos

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check if backend is running on port 8000
   - Verify WebSocket URL in environment variables
   - Check browser console for errors

2. **Microphone Permission Denied**
   - Grant microphone permissions in browser
   - Check browser security settings
   - Ensure HTTPS in production

3. **Audio Not Recording**
   - Check microphone hardware
   - Verify browser compatibility
   - Check console for WebRTC errors

### Debug Mode

Enable debug mode by setting `REACT_APP_DEBUG=true` in your environment variables.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
