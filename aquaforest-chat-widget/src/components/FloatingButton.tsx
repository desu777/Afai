import React from 'react';
import { MessageCircle, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface FloatingButtonProps {
  isOpen: boolean;
  onClick: () => void;
  position?: 'bottom-right' | 'bottom-left';
}

export const FloatingButton: React.FC<FloatingButtonProps> = ({ 
  isOpen, 
  onClick
}) => {
  return (
    <AnimatePresence mode="wait">
      <motion.button
        key={isOpen ? 'close' : 'open'}
        className={`af-floating-button ${!isOpen ? 'pulse' : ''} ${isOpen ? 'is-open' : ''}`}
        onClick={onClick}
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0, opacity: 0 }}
        transition={{
          type: 'spring',
          stiffness: 200,
          damping: 20
        }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        {isOpen ? (
          <X size={20} />
        ) : (
          <MessageCircle size={20} />
        )}
      </motion.button>
    </AnimatePresence>
  );
};