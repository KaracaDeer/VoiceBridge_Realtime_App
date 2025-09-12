import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Wifi, WifiOff, AlertCircle, CheckCircle } from 'lucide-react';
import './ConnectionStatus.css';

const ConnectionStatus = ({ isConnected }) => {
  const getStatusInfo = () => {
    if (isConnected) {
      return {
        icon: CheckCircle,
        text: 'Connected',
        color: '#22c55e',
        bgColor: 'rgba(34, 197, 94, 0.2)',
        borderColor: 'rgba(34, 197, 94, 0.3)'
      };
    } else {
      return {
        icon: WifiOff,
        text: 'Disconnected',
        color: '#ef4444',
        bgColor: 'rgba(239, 68, 68, 0.2)',
        borderColor: 'rgba(239, 68, 68, 0.3)'
      };
    }
  };

  const statusInfo = getStatusInfo();
  const IconComponent = statusInfo.icon;

  return (
    <AnimatePresence>
      <motion.div
        className="connection-status"
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0, opacity: 0 }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        style={{
          backgroundColor: statusInfo.bgColor,
          borderColor: statusInfo.borderColor
        }}
      >
        <motion.div
          className="status-icon"
          animate={{
            scale: isConnected ? [1, 1.2, 1] : 1,
            rotate: isConnected ? [0, 5, -5, 0] : 0
          }}
          transition={{
            duration: 2,
            repeat: isConnected ? Infinity : 0,
            ease: "easeInOut"
          }}
        >
          <IconComponent 
            size={20} 
            color={statusInfo.color}
          />
        </motion.div>
        
        <motion.span
          className="status-text"
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.1 }}
        >
          {statusInfo.text}
        </motion.span>

        {isConnected && (
          <motion.div
            className="status-pulse"
            animate={{
              scale: [1, 1.5, 1],
              opacity: [0.5, 0, 0.5]
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        )}
      </motion.div>
    </AnimatePresence>
  );
};

export default ConnectionStatus;
