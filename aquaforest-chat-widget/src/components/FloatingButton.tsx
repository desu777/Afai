import React from 'react';
import { MessageCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { useIsMobile } from '../hooks/useIsMobile';
import { useTranslation } from '../hooks/useTranslation';

interface FloatingButtonProps {
  isOpen: boolean;
  onClick: () => void;
  position?: 'bottom-right' | 'bottom-left';
  showCallToAction?: boolean;
}

export const FloatingButton: React.FC<FloatingButtonProps> = ({ 
  isOpen, 
  onClick,
  showCallToAction = false
}) => {
  const isMobile = useIsMobile();
  const { t } = useTranslation();
  
  // Ukryj floating button gdy widget jest otwarty (X jest teraz w oknach)
  if (isOpen) {
    return null;
  }
  
  return (
    <div className="af-floating-button-container">
      {/* Call to Action Bubble - tylko na mobile gdy zamknięty */}
      {isMobile && (
        <div
          className={`af-cta-bubble ${showCallToAction ? 'af-visible' : ''}`}
          onClick={onClick}
        >
          <span className="af-cta-text">{t.callToAction.askAfai}</span>
        </div>
      )}

      {/* Główny przycisk floating - tylko MessageCircle (do otwierania) */}
      <motion.button
        className="af-floating-button pulse"
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
        <MessageCircle size={20} />
      </motion.button>
    </div>
  );
};