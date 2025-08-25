import { useState, useEffect } from 'react'
import { Loader2 } from 'lucide-react'

const LoadingMessage: React.FC = () => {
  const thinkingTopics = [
    "corals",
    "reef chemistry", 
    "calcium levels",
    "marine salts",
    "SPS corals",
    "water parameters",
    "beneficial bacteria",
    "dosing calculations",
    "coral nutrition",
    "aquascaping rocks",
    "trace elements",
    "marine supplements",
    "reef lighting",
    "water circulation",
    "biological filtration"
  ];

  const [currentTopicIndex, setCurrentTopicIndex] = useState(0);
  const [dots, setDots] = useState('');
  const [isChanging, setIsChanging] = useState(false);

  const currentTopic = thinkingTopics[currentTopicIndex];

  useEffect(() => {
    // Animate dots and change topic after 2 full cycles
      const dotsInterval = setInterval(() => {
        setDots(prev => {
        if (prev === '...') {
          // Completed a cycle, change topic with animation
          setIsChanging(true);
          
          // After fade out completes, change topic and fade in
          setTimeout(() => {
            setCurrentTopicIndex(prevIndex => (prevIndex + 1) % thinkingTopics.length);
            setTimeout(() => {
              setIsChanging(false);
            }, 100); // Small delay before fade in
          }, 300); // Duration of fade out
          
          return '';
        }
          return prev + '.';
        });
    }, 500); // 500ms per dot for smooth animation

      return () => clearInterval(dotsInterval);
  }, [thinkingTopics.length]);

  return (
    <div className="flex justify-start mb-4 sm:mb-6">
      <div className="flex items-start space-x-2 sm:space-x-4 max-w-[90%] sm:max-w-3xl w-full">
        {/* Avatar - ukryty na mobile */}
        <div className="hidden sm:flex w-10 h-10 rounded-lg bg-brand-600 items-center justify-center shadow-sm flex-shrink-0 animate-float">
          <div className="circle">
            <div className="wave"></div>
          </div>
        </div>
        
        <div className="rounded-2xl px-4 py-3 sm:px-6 sm:py-4 bg-white/95 backdrop-blur-md border border-brand-200/40 shadow-sm hover:shadow-lg transition-all duration-300 flex-1 min-w-0">
          <div className="flex items-center space-x-2 sm:space-x-3">
            <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 text-brand-600 animate-spin flex-shrink-0" />
            <span className="text-gray-700 text-xs sm:text-sm font-medium break-words">
              I'm thinking about{' '}
              <span 
                className={`transition-all duration-300 ease-in-out ${
                  isChanging ? 'opacity-0 transform translate-y-1' : 'opacity-100 transform translate-y-0'
                }`}
              >
                {currentTopic}
              </span>
              {dots}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingMessage 