import React from 'react';
import { motion } from 'framer-motion';
import { X } from 'lucide-react';

interface WelcomeScreenProps {
  onStart: () => void;
  onClose: () => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onStart, onClose }) => {
  return (
    <motion.div 
      className="af-welcome-screen"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="af-welcome-content">
        <div className="af-welcome-group">
          <motion.h2 
            className="af-welcome-title"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
          >
            Meet Afai
          </motion.h2>

          <motion.div 
            className="af-welcome-icon"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ 
              type: "spring",
              stiffness: 200,
              damping: 20,
              delay: 0.3 
            }}
          >
            <div className="af-circle">
              <div className="af-wave-inner"></div>
            </div>
          </motion.div>

          <motion.p 
            className="af-welcome-subtitle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.5 }}
          >
            Wisdom from the reef's heart...
          </motion.p>
        </div>

        <motion.button
          className="af-welcome-button"
          onClick={onStart}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          whileHover={{ scale: 1.05, y: -2 }}
          whileTap={{ scale: 0.95 }}
        >
          Ask Afai in any language!
        </motion.button>
      </div>

      <motion.div 
        className="af-welcome-footer"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
      >
        Afai by Aquaforest
      </motion.div>
    </motion.div>
  );
};