import { useState, useEffect } from 'react'
import { Loader2, Clock, CheckCircle, AlertCircle } from 'lucide-react'
import { WorkflowUpdate } from '../types'

interface StreamingLoadingMessageProps {
  currentUpdate?: WorkflowUpdate;
}

const StreamingLoadingMessage: React.FC<StreamingLoadingMessageProps> = ({ currentUpdate }) => {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [startTime] = useState(Date.now());

  // Update elapsed time - use either backend time or local timer
  useEffect(() => {
    const interval = setInterval(() => {
      if (currentUpdate?.elapsed_time) {
        setElapsedTime(currentUpdate.elapsed_time);
      } else {
        // Fallback to local timer if no backend time
        setElapsedTime((Date.now() - startTime) / 1000);
      }
    }, 100); // Update every 100ms for smooth progress

    return () => clearInterval(interval);
  }, [currentUpdate?.elapsed_time, startTime]);

  // Workflow steps for progress indication (updated with correct node names)
  const workflowSteps = [
    { node: 'start', label: 'Starting analysis' },
    { node: 'detect_intent', label: 'Understanding question' },
    { node: 'load_products', label: 'Loading products' },
    { node: 'business_reasoner', label: 'Analyzing needs' },
    { node: 'optimize_query', label: 'Finding products' },
    { node: 'search_pinecone', label: 'Searching catalog' },
    { node: 'evaluate_confidence', label: 'Validating results' },
    { node: 'format_response', label: 'Preparing response' },
    { node: 'complete', label: 'Complete' }
  ];

  // Simple progress calculation - just increment when we get updates
  const getSimpleProgress = () => {
    if (!currentUpdate) return 0;
    
    // Map some common nodes to approximate progress
    const progressMap: Record<string, number> = {
      'start': 5,
      'detect_intent': 15,
      'load_products': 25,
      'business_reasoner': 40,
      'optimize_query': 55,
      'search_pinecone': 70,
      'evaluate_confidence': 85,
      'format_response': 95,
      'follow_up_router': 30,
      'handle_follow_up': 90,
      'escalate_support': 100,
      'complete': 100
    };
    
    return progressMap[currentUpdate.node] || Math.min(90, elapsedTime * 2); // Fallback: 2% per second, max 90%
  };

  const progress = getSimpleProgress();
  const currentStep = workflowSteps.findIndex(step => step.node === currentUpdate?.node) + 1;

  const formatTime = (seconds: number) => {
    return `${seconds.toFixed(1)}s`;
  };

  const getStatusIcon = () => {
    if (!currentUpdate) return <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 text-purple-600 animate-spin" />;
    
    switch (currentUpdate.status) {
      case 'complete':
        return <CheckCircle className="w-4 h-4 sm:w-5 sm:h-5 text-green-600" />;
      case 'error':
        return <AlertCircle className="w-4 h-4 sm:w-5 sm:h-5 text-red-600" />;
      default:
        return <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 text-purple-600 animate-spin" />;
    }
  };

  const getMessage = () => {
    if (!currentUpdate) return "Preparing to analyze your question...";
    return currentUpdate.message;
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

  return (
    <div className="flex justify-start mb-6">
      <div className="flex items-start space-x-3 sm:space-x-4 max-w-3xl w-full">
        <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl sm:rounded-2xl bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 flex items-center justify-center shadow-md flex-shrink-0">
          <div className="circle">
            <div className="wave"></div>
          </div>
        </div>
        
        <div className="rounded-2xl sm:rounded-3xl px-4 py-3 sm:px-6 sm:py-4 bg-white/95 backdrop-blur-md border border-purple-200/40 shadow-sm flex-1 min-w-0">
          {/* Status Message with Icon */}
          <div className="flex items-center space-x-2 sm:space-x-3 mb-3">
            {getStatusIcon()}
            <span className={`text-xs sm:text-sm font-medium break-words flex-1 ${getStatusColor()}`}>
              {getMessage()}
            </span>
            
            {/* Timer */}
            <div className="flex items-center space-x-1 text-xs text-gray-500 flex-shrink-0">
              <Clock className="w-3 h-3" />
              <span>{formatTime(elapsedTime)}</span>
            </div>
          </div>

          {/* Progressive steps indicator */}
          {currentUpdate?.status !== 'complete' && currentUpdate?.status !== 'error' && (
            <div className="space-y-2">
              {/* Progress Bar */}
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <div 
                  className="bg-gradient-to-r from-purple-600 to-violet-600 h-1.5 rounded-full transition-all duration-500 ease-out"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>

              {/* Step indicators */}
              <div className="flex justify-between text-xs text-gray-500">
                <span className="text-left">
                  Processing...
                </span>
                <span className="text-right">
                  {progress.toFixed(0)}% complete
                </span>
              </div>
            </div>
          )}

          {/* Success/Error state - no progress bar */}
          {(currentUpdate?.status === 'complete' || currentUpdate?.status === 'error') && (
            <div className="text-xs text-gray-500 text-center mt-2">
              {currentUpdate.status === 'complete' ? '✨ Analysis complete!' : '⚠️ An error occurred'}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default StreamingLoadingMessage; 