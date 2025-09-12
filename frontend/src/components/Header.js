import React from 'react';
import { motion } from 'framer-motion';
import { Mic, Trash2, Volume2 } from 'lucide-react';
import './Header.css';

const Header = ({ isConnected, onClearTranscriptions }) => {
  return (
    <motion.header
      className="header"
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
    >
      <div className="header-content">
        <motion.div
          className="logo-section"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <motion.div
            className="logo-icon"
            animate={{
              rotate: [0, 5, -5, 0],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          >
            <Volume2 size={32} />
          </motion.div>
          <div className="logo-text">
            <h1 className="app-title">VoiceBridge</h1>
            <p className="app-subtitle">Real-time Speech-to-Text</p>
          </div>
        </motion.div>

        <motion.div
          className="header-actions"
          initial={{ x: 50, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.3 }}
        >
          <motion.button
            className="clear-button"
            onClick={onClearTranscriptions}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            title="Clear all transcriptions"
          >
            <Trash2 size={20} />
            <span>Clear</span>
          </motion.button>

          <motion.div
            className={`connection-indicator ${isConnected ? 'connected' : 'disconnected'}`}
            animate={{
              scale: isConnected ? [1, 1.1, 1] : 1,
            }}
            transition={{
              duration: 2,
              repeat: isConnected ? Infinity : 0,
              ease: "easeInOut"
            }}
          >
            <div className="indicator-dot" />
            <span className="indicator-text">
              {isConnected ? 'Connected' : 'Disconnected'}
            </span>
          </motion.div>
        </motion.div>
      </div>

      <motion.div
        className="header-divider"
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ duration: 0.8, delay: 0.4 }}
      />
    </motion.header>
  );
};

export default Header;
