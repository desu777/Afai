import { useState, useEffect } from 'react'
import { Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { ThreeDot } from 'react-loading-indicators'
import BlurText from './BlurText'
import { WorkflowUpdate } from '../types'

interface StreamingLoadingMessageProps {
  currentUpdate?: WorkflowUpdate;
}

const StreamingLoadingMessage: React.FC<StreamingLoadingMessageProps> = ({ currentUpdate }) => {
  const [liveTimer, setLiveTimer] = useState(1);
  const [previousProgress, setPreviousProgress] = useState(0);
  const [dotCount, setDotCount] = useState(1);
  const [finalThoughtTime, setFinalThoughtTime] = useState<number | null>(null);
  const [currentMessage, setCurrentMessage] = useState("");
  const [animationKey, setAnimationKey] = useState(0);

  // Live timer - counts 1, 2, 3, 4, 5...
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveTimer(prev => prev + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  // Progressive dots animation
  useEffect(() => {
    if (currentUpdate?.status === 'complete' || currentUpdate?.status === 'error') {
      return; // Stop dots animation when complete
    }

    const interval = setInterval(() => {
      setDotCount(prev => prev >= 4 ? 1 : prev + 1);
    }, 500);

    return () => clearInterval(interval);
  }, [currentUpdate?.status]);

  // Capture final thought time when complete
  useEffect(() => {
    if (currentUpdate?.status === 'complete' && finalThoughtTime === null) {
      setFinalThoughtTime(liveTimer);
    }
  }, [currentUpdate?.status, liveTimer, finalThoughtTime]);

  // Workflow steps for progress indication
  const nodeInfo = [
    { node: 'detect_intent_and_language', label: 'Understanding your query' },
    { node: 'load_product_names', label: 'Loading product catalog' },
    { node: 'business_reasoner', label: 'Analyzing your needs' },
    { node: 'optimize_product_query', label: 'Optimizing search strategy' },
    { node: 'search_products_k20', label: 'Searching through products' },
    { node: 'format_final_response', label: 'Crafting detailed response' },
    
    { node: 'handle_follow_up', label: 'Processing follow-up' },
    { node: 'follow_up_router', label: 'Analyzing conversation context' }
  ];

  // Simple progress calculation
  const getSimpleProgress = () => {
    if (!currentUpdate) return 0;
    
    const nodeProgressMap: Record<string, number> = {
      'detect_intent_and_language': 15,
      'load_product_names': 25,
      'business_reasoner': 45,
      'optimize_product_query': 55,
      'search_products_k20': 75,
      'format_final_response': 95,

      'handle_follow_up': 95,
      'follow_up_router': 35
    };
    
    const mappedProgress = nodeProgressMap[currentUpdate.node];
    const fallbackProgress = Math.min(90, liveTimer * 3);
    
    if ((import.meta.env as any).VITE_TEST_ENV === 'true') {
      console.log(`📈 [Progress] Node: ${currentUpdate.node}, Mapped: ${mappedProgress}, Fallback: ${fallbackProgress}`);
    }
    
    return mappedProgress || fallbackProgress;
  };

  const progress = getSimpleProgress();
  
  // Track progress changes with smooth animation
  useEffect(() => {
    if (progress !== previousProgress) {
      const direction = progress > previousProgress ? 'forward' : 'backward';
      console.log(`📈 [Progress] Progress ${direction}: ${previousProgress}% → ${progress}% (node: ${currentUpdate?.node})`);
      setPreviousProgress(progress);
    }
  }, [progress, previousProgress, currentUpdate?.node]);

  // Track message changes and trigger re-animation
  useEffect(() => {
    const newMessage = getMessage();
    if (newMessage !== currentMessage) {
      console.log(`🎭 [Stage Change] "${currentMessage}" → "${newMessage}"`);
      setCurrentMessage(newMessage);
      setAnimationKey(prev => prev + 1); // Force BlurText re-render
    }
  }, [currentUpdate?.node, currentUpdate?.status, liveTimer, finalThoughtTime]);

  const getDots = () => '.'.repeat(dotCount);

  const getStatusIcon = () => {
    if (!currentUpdate) {
      return (
        <ThreeDot 
          variant="pulsate"
          color="#7c3aed" 
          size="small" 
          text="" 
          textColor="" 
        />
      );
    }
    
    switch (currentUpdate.status) {
      case 'complete':
        return <CheckCircle className="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6 text-green-600 flex-shrink-0" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 sm:w-5 sm:h-5 md:w-6 md:h-6 text-red-600 flex-shrink-0" />;
      default:
        return (
          <ThreeDot 
            variant="pulsate"
            color="#7c3aed" 
            size="small" 
            text="" 
            textColor="" 
          />
        );
    }
  };

  const getMessage = () => {
    if (!currentUpdate) return "Preparing to analyze your question";
    
    if (currentUpdate.status === 'complete') {
      return `AF <thought ${finalThoughtTime || liveTimer}s for prepared complex answer>`;
    }
    
    // Find human-readable label for current node
    const nodeLabel = nodeInfo.find(info => info.node === currentUpdate.node)?.label;
    return nodeLabel || currentUpdate.message;
  };

  const getStatusColor = () => {
    if (!currentUpdate) return "text-gray-700";
    
    switch (currentUpdate.status) {
      case 'complete':
        return "text-green-700";
      case 'error':
        return "text-red-700";
      default:
        return "text-gray-700";
    }
  };

  // Handle animation completion
  const handleAnimationComplete = () => {
    if ((import.meta.env as any).VITE_TEST_ENV === 'true') {
      console.log('✨ [BlurText] Animation completed!');
    }
  };

  // Check if motion should be reduced
  const prefersReducedMotion = typeof window !== 'undefined' && 
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  return (
    <div className="flex justify-start mb-4 sm:mb-6">
      <div className="flex items-start space-x-2 sm:space-x-4 max-w-[90%] sm:max-w-3xl w-full">
        {/* Avatar - ukryty na mobile */}
        <div className="hidden sm:flex w-10 h-10 rounded-2xl bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 items-center justify-center shadow-md flex-shrink-0">
          <div className="circle">
            <div className="wave"></div>
          </div>
        </div>
        
        <div className="rounded-2xl sm:rounded-3xl px-4 py-3 sm:px-6 sm:py-4 bg-white/95 backdrop-blur-md border border-purple-200/40 shadow-sm flex-1 min-w-0">
          {/* Status Message with Icon */}
          <div className="flex items-start space-x-3 sm:space-x-4 mb-4">
            <div className="flex-shrink-0 mt-1">
              {getStatusIcon()}
            </div>
            
            <div className="flex-1 min-w-0">
              {/* Animated Text Message with Re-animation */}
              {prefersReducedMotion ? (
                <div className={`text-sm sm:text-base md:text-lg font-semibold break-words ${getStatusColor()}`}>
                  {getMessage()}{currentUpdate?.status !== 'complete' && currentUpdate?.status !== 'error' && getDots()}
                </div>
              ) : (
                <BlurText
                  key={animationKey}
                  text={getMessage() + (currentUpdate?.status !== 'complete' && currentUpdate?.status !== 'error' ? getDots() : '')}
                  delay={50}
                  className={`text-sm sm:text-base md:text-lg font-semibold break-words ${getStatusColor()}`}
                  onAnimationComplete={handleAnimationComplete}
                />
              )}
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-3">
            <div className="flex justify-between items-center text-xs text-gray-500 mb-2">
              <span>Progress</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-purple-600 to-violet-700 h-2 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>

          {/* Timing Information */}
          <div className="flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center space-x-1">
              <Clock className="w-3 h-3" />
              <span>Thinking: {liveTimer}s</span>
            </div>
            
            {/* Show node timing only when complete or error */}
            {currentUpdate?.elapsed_time && (currentUpdate?.status === 'complete' || currentUpdate?.status === 'error') && (
              <span>Node: {(currentUpdate.elapsed_time / 1000).toFixed(1)}s</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default StreamingLoadingMessage; 