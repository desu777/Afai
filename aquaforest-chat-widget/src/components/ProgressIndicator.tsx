import React, { useState, useEffect } from 'react';
import { WorkflowUpdate } from '../types';

interface ProgressIndicatorProps {
  currentUpdate?: WorkflowUpdate;
}

// Node messages mapping (poetic, ocean-inspired messages for widget)
const nodeMessages: Record<string, string[]> = {
  'detect_intent_and_language': [
    "Listening to your question",
    "Sensing your reef's whispers", 
    "Tuning into ocean's frequency"
  ],
  'business_reasoner': [
    "Gathering ocean's wisdom",
    "Reading the coral's language",
    "Diving into the matter"
  ],
  'optimize_product_query': [
    "Focusing sea's energy",
    "Charting knowledge course",
    "Drawing treasure map"
  ],
  'search_products_k20': [
    "Diving for information pearls",
    "Searching knowledge currents", 
    "Exploring Aquaforest libraries"
  ],
  'format_final_response': [
    "Translating reef's whisper",
    "Polishing final details",
    "Weaving the answer"
  ],
  'handle_follow_up': [
    "Connecting conversation currents",
    "Tracing dialogue through waters",
    "Weaving discussion threads"
  ],
  'follow_up_router': [
    "Navigating context streams",
    "Reading conversation patterns",
    "Mapping thought constellation"
  ]
};

// Progress mapping (simplified for widget)
const nodeProgress: Record<string, number> = {
  'detect_intent_and_language': 20,
  'business_reasoner': 40,
  'optimize_product_query': 60,
  'search_products_k20': 80,
  'format_final_response': 95,
  'handle_follow_up': 95,
  'follow_up_router': 35
};

export const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({ currentUpdate }) => {
  const [liveTimer, setLiveTimer] = useState(1);
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const [messageRotationTimer, setMessageRotationTimer] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);
  const [animationKey, setAnimationKey] = useState(0);
  const [dotCount, setDotCount] = useState(1);

  // Live timer - counts 1, 2, 3, 4, 5...
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveTimer(prev => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Message rotation timer
  useEffect(() => {
    const interval = setInterval(() => {
      setMessageRotationTimer(prev => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Progressive dots animation (like frontend)
  useEffect(() => {
    if (currentUpdate?.status === 'complete' || currentUpdate?.status === 'error') {
      return; // Stop dots animation when complete
    }

    const interval = setInterval(() => {
      setDotCount(prev => prev >= 3 ? 1 : prev + 1); // Widget: max 3 dots
    }, 500);

    return () => clearInterval(interval);
  }, [currentUpdate?.status]);

  // Rotate message every 5 seconds with smooth fade animation
  useEffect(() => {
    let fadeOutTimeout: NodeJS.Timeout;
    let fadeInTimeout: NodeJS.Timeout;

    if (messageRotationTimer > 0 && messageRotationTimer % 5 === 0 && currentUpdate?.node) {
      const messages = nodeMessages[currentUpdate.node];
      if (messages && messages.length > 0) {
        // Start fade out animation
        setIsAnimating(true);
        
        fadeOutTimeout = setTimeout(() => {
          // Change message after fade out using callback form
          setCurrentMessageIndex(prevIndex => {
            let newIndex = Math.floor(Math.random() * messages.length);
            if (messages.length > 1 && newIndex === prevIndex) {
              newIndex = (newIndex + 1) % messages.length;
            }
            return newIndex;
          });
          setAnimationKey(prev => prev + 1);
          
          // Start fade in animation
          fadeInTimeout = setTimeout(() => {
            setIsAnimating(false);
          }, 50); // Quick fade in
        }, 200); // Fade out duration
      }
    }

    // Cleanup timeouts on unmount or dependency change
    return () => {
      clearTimeout(fadeOutTimeout);
      clearTimeout(fadeInTimeout);
    };
  }, [messageRotationTimer, currentUpdate?.node]);

  // Reset message rotation when stage changes
  useEffect(() => {
    if (currentUpdate?.node) {
      const messages = nodeMessages[currentUpdate.node];
      if (messages && messages.length > 0) {
        const randomIndex = Math.floor(Math.random() * messages.length);
        setCurrentMessageIndex(randomIndex);
        setMessageRotationTimer(0);
        setIsAnimating(false); // Reset animation state
        setAnimationKey(prev => prev + 1); // Trigger re-render
        setDotCount(1); // Reset dots when stage changes
      }
    }
  }, [currentUpdate?.node]);

  const getDots = () => '.'.repeat(dotCount);

  const getProgress = (): number => {
    if (!currentUpdate) return 0;
    
    const mappedProgress = nodeProgress[currentUpdate.node];
    const fallbackProgress = Math.min(90, liveTimer * 3);
    
    return mappedProgress || fallbackProgress;
  };

  const getMessage = (): string => {
    if (!currentUpdate) return "Preparing to analyze your question" + getDots();
    
    if (currentUpdate.status === 'complete') {
      return `Response ready! (${liveTimer}s)`;
    }
    
    if (currentUpdate.status === 'error') {
      return "Processing error occurred";
    }
    
    // Use rotating messages with animated dots
    const messages = nodeMessages[currentUpdate.node];
    if (messages && messages.length > 0) {
      return messages[currentMessageIndex] + getDots();
    }
    
    // Fallback to current update message with dots
    return (currentUpdate.message || "Processing") + getDots();
  };

  const progress = getProgress();

  return (
    <div className="af-progress-indicator">
      {/* Icon Section */}
      <div className="af-progress-icon">
        <div className="af-circle">
          <div className="af-wave-inner"></div>
        </div>
      </div>
      
      {/* Content Section */}
      <div className="af-progress-content">
        {/* Message and Progress Row */}
        <div className="af-progress-row">
          <span 
            key={animationKey}
            className={`af-progress-text ${isAnimating ? 'af-progress-text-fade' : ''}`}
          >
            {getMessage()}
          </span>
          <span className="af-progress-percentage">{Math.round(progress)}%</span>
        </div>
        
        {/* Progress Bar */}
        <div className="af-progress-bar-container">
          <div 
            className="af-progress-bar-fill"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        
        {/* Timer */}
        <div className="af-progress-timer">
          Thinking: {liveTimer}s
        </div>
      </div>
    </div>
  );
};