import React from 'react';
import { motion } from 'framer-motion';

interface WelcomeScreenProps {
  onStart: () => void;
}

export const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onStart }) => {
  return (
    <motion.div 
      className="af-welcome-screen"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <motion.div 
        className="af-welcome-icon"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ 
          type: "spring",
          stiffness: 200,
          damping: 20,
          delay: 0.2 
        }}
      >
        <div className="af-wave" />
        <svg 
          viewBox="0 0 24 24" 
          width="40" 
          height="40" 
          fill="none"
          style={{ position: 'relative', zIndex: 1 }}
        >
          <path
            d="M5 12C5 16.97 8.03 21 12 21C12.45 21 12.89 20.96 13.32 20.88C13.12 20.46 13 20 13 19.5C13 18.12 14.12 17 15.5 17C16.34 17 17.08 17.43 17.5 18.1C19.04 16.8 20 14.97 20 12.9C20 10.32 18.82 8.03 17 6.63C16.94 5.17 15.74 4 14.27 4C13.33 4 12.53 4.59 12.2 5.41C8.84 5.86 6.24 8.24 5.28 11.35C5.1 11.55 5 11.77 5 12Z"
            fill="white"
            stroke="white"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M12 8.5C12 7.67 11.33 7 10.5 7C9.67 7 9 7.67 9 8.5C9 9.33 9.67 10 10.5 10C11.33 10 12 9.33 12 8.5Z"
            fill="#47154C"
          />
          <motion.path
            d="M3 12C3 12 4 10 4 8C4 6 3 4 3 4"
            stroke="white"
            strokeWidth="1.5"
            strokeLinecap="round"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ 
              duration: 2,
              repeat: Infinity,
              repeatType: "reverse",
              ease: "easeInOut"
            }}
          />
          <motion.path
            d="M21 12C21 12 22 10 22 8C22 6 21 4 21 4"
            stroke="white"
            strokeWidth="1.5"
            strokeLinecap="round"
            initial={{ pathLength: 0, opacity: 0 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ 
              duration: 2,
              repeat: Infinity,
              repeatType: "reverse",
              ease: "easeInOut",
              delay: 0.5
            }}
          />
        </svg>
      </motion.div>

      <motion.h2 
        className="af-welcome-title"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4 }}
      >
        Meet Afai
      </motion.h2>

      <motion.p 
        className="af-welcome-subtitle"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
      >
        Wisdom from the reef's heart...
      </motion.p>

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
    </motion.div>
  );
};