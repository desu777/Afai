import { useState, useEffect } from 'react'
import { Loader2 } from 'lucide-react'

const LoadingMessage: React.FC = () => {
  const oceanMessages = [
    "Diving for knowledge in ocean depths",
    "Consulting coral reef experts",
    "Analyzing water parameters in laboratory", 
    "Checking latest SPS research",
    "Preparing professional diagnosis",
    "Testing calcium levels in marine ecosystem",
    "Studying beneficial bacteria cultures",
    "Calibrating dosing pump calculations",
    "Examining coral polyp feeding patterns",
    "Researching optimal lighting spectrum data"
  ];

  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const [displayedText, setDisplayedText] = useState('');
  const [charIndex, setCharIndex] = useState(0);
  const [dots, setDots] = useState('');
  const [isTyping, setIsTyping] = useState(true);

  const currentFullMessage = oceanMessages[currentMessageIndex];

  useEffect(() => {
    // Typewriter effect
    if (isTyping && charIndex < currentFullMessage.length) {
      const typingTimeout = setTimeout(() => {
        setDisplayedText(currentFullMessage.slice(0, charIndex + 1));
        setCharIndex(prev => prev + 1);
      }, 60); // 60ms per character for smooth typing

      return () => clearTimeout(typingTimeout);
    } else if (charIndex >= currentFullMessage.length) {
      // Finished typing, wait 3 seconds then switch to next message
      setIsTyping(false);
      const switchTimeout = setTimeout(() => {
        setCurrentMessageIndex(prev => (prev + 1) % oceanMessages.length);
        setCharIndex(0);
        setDisplayedText('');
        setIsTyping(true);
      }, 3000);

      return () => clearTimeout(switchTimeout);
    }
  }, [charIndex, currentFullMessage, isTyping]);

  useEffect(() => {
    // Animate dots only when not typing or when typing is complete
    if (!isTyping || charIndex >= currentFullMessage.length) {
      const dotsInterval = setInterval(() => {
        setDots(prev => {
          if (prev === '...') return '';
          return prev + '.';
        });
      }, 400);

      return () => clearInterval(dotsInterval);
    } else {
      setDots('');
    }
  }, [isTyping, charIndex, currentFullMessage.length]);

  return (
    <div className="flex justify-start mb-6">
      <div className="flex items-start space-x-4 max-w-3xl">
        <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 flex items-center justify-center shadow-md">
          <div className="circle">
            <div className="wave"></div>
          </div>
        </div>
        <div className="rounded-3xl px-6 py-4 bg-white/95 backdrop-blur-md border border-purple-200/40 shadow-sm">
          <div className="flex items-center space-x-3">
            <Loader2 className="w-5 h-5 text-purple-600 animate-spin" />
            <span className="text-gray-700 text-sm font-medium">
              {displayedText}{dots}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingMessage 