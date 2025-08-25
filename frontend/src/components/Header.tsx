import { useState, useEffect, useRef } from 'react'
import { MoreVertical, MessageSquarePlus, BarChart3, Send, FileText } from 'lucide-react'
import FeedbackModal from './FeedbackModal'

interface HeaderProps {
  accessLevel: 'visionary_expert' | 'admin';
  onViewChange?: (view: 'chat' | 'feedback' | 'analytics') => void;
  activeView?: 'chat' | 'feedback' | 'analytics';
}

const Header: React.FC<HeaderProps> = ({ accessLevel, onViewChange, activeView = 'chat' }) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const closeMobileMenu = () => {
    setIsClosing(true);
    setTimeout(() => {
      setIsMobileMenuOpen(false);
      setIsClosing(false);
    }, 150); // Animation duration
  };

  const openFeedbackModal = () => {
    setIsFeedbackModalOpen(true);
    if (isMobileMenuOpen) {
      closeMobileMenu();
    }
  };

  const closeFeedbackModal = () => {
    setIsFeedbackModalOpen(false);
  };

  const handleViewChange = (view: 'chat' | 'feedback' | 'analytics') => {
    onViewChange?.(view);
    if (isMobileMenuOpen) {
      closeMobileMenu();
    }
  };

  const getButtonClass = (view: 'chat' | 'feedback' | 'analytics') => {
    const baseClass = "flex items-center space-x-2 px-3 py-2 rounded-xl transition-all duration-200 hover:scale-105 text-sm font-medium";
    const activeClass = "bg-gray-100 text-brand-700 border border-gray-200";
    const inactiveClass = "text-gray-700 hover:bg-gray-100 hover:text-brand-700";
    
    return `${baseClass} ${activeView === view ? activeClass : inactiveClass}`;
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        closeMobileMenu();
      }
    };

    if (isMobileMenuOpen && !isClosing) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isMobileMenuOpen, isClosing]);

  return (
    <div className="bg-white/95 backdrop-blur-md border-b border-gray-200/50 px-4 sm:px-6 py-5 shadow-sm relative z-50">
      <div className="flex items-center justify-between max-w-5xl mx-auto">
        <div className="flex items-center space-x-4">
          <div className="w-12 h-12 bg-brand-600 rounded-lg flex items-center justify-center shadow-lg overflow-hidden">
            <img 
              src="/horse.png" 
              alt="Konik morski" 
              className="w-8 h-8 object-contain"
            />
          </div>
          <div className="flex flex-col justify-center">
            <div className="h-10 sm:h-12 lg:h-16">
              <svg viewBox="0 0 160 40" className="w-full h-full max-w-[240px] sm:max-w-[300px] lg:max-w-[360px]">
                <defs>
                  <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style={{stopColor: '#9333ea'}} />
                    <stop offset="50%" style={{stopColor: '#7c3aed'}} />
                    <stop offset="100%" style={{stopColor: '#5b21b6'}} />
                  </linearGradient>
                  <pattern id="wave" x="0" y="-0.5" width="100%" height="100%" patternUnits="userSpaceOnUse">
                    <path id="wavePath" d="M-40 20 Q-30 16 -20 20 T0 20 T20 20 T40 20 T60 20 T80 20 T100 20 T120 20 T140 20 T160 20 T180 20 V40 H-40z" fill="url(#gradient)">
                      <animateTransform
                        attributeName="transform"
                        begin="0s"
                        dur="2s"
                        type="translate"
                        from="0,0"
                        to="40,0"
                        repeatCount="indefinite" />
                    </path>
                  </pattern>
                </defs>
                <text textAnchor="middle" x="80" y="28" fontSize="22" fontWeight="bold" fill="#1f2937" fillOpacity="0.15">Afai by Aquaforest</text>
                <text textAnchor="middle" x="80" y="28" fontSize="22" fontWeight="bold" fill="url(#wave)" fillOpacity="1">Afai by Aquaforest</text>
              </svg>
            </div>
          </div>
        </div>
        {/* Desktop Menu */}
        <div className="hidden md:flex items-center space-x-3">
          <button 
            onClick={() => handleViewChange('chat')}
            className={getButtonClass('chat')}
          >
            <MessageSquarePlus className="w-4 h-4" />
            <span>New chat</span>
          </button>
          <button 
            onClick={openFeedbackModal}
            className="flex items-center space-x-2 px-3 py-2 hover:bg-gray-100 rounded-xl transition-all duration-200 hover:scale-105 text-sm font-medium text-gray-700 hover:text-brand-700"
          >
            <Send className="w-4 h-4" />
            <span>Feedback</span>
          </button>
          {accessLevel === 'admin' && (
            <>
              <button 
                onClick={() => handleViewChange('feedback')}
                className={getButtonClass('feedback')}
              >
                <FileText className="w-4 h-4" />
                <span>ReadFeedback</span>
              </button>
              <button 
                onClick={() => handleViewChange('analytics')}
                className={getButtonClass('analytics')}
              >
                <BarChart3 className="w-4 h-4" />
                <span>Analysis</span>
              </button>
            </>
          )}
        </div>

        {/* Mobile Menu */}
        <div className="md:hidden relative" ref={menuRef}>
          <button 
            onClick={() => {
              if (isMobileMenuOpen) {
                closeMobileMenu();
              } else {
                setIsMobileMenuOpen(true);
              }
            }}
            className="p-2.5 hover:bg-gray-100 rounded-xl transition-all duration-200 hover:scale-105"
          >
            <MoreVertical className="w-5 h-5 text-gray-600" />
          </button>
          
          {/* Mobile Dropdown */}
          {isMobileMenuOpen && (
            <div className={`fixed right-4 top-20 w-48 bg-white/95 backdrop-blur-md border border-gray-200/50 rounded-xl shadow-xl z-[99999] ${
              isClosing ? 'animate-dropdown-out' : 'animate-dropdown-in'
            }`}>
              <div className="py-2">
                <button 
                  onClick={() => handleViewChange('chat')}
                  className={`flex items-center space-x-3 w-full px-4 py-3 hover:bg-gray-50 transition-colors text-sm font-medium ${
                    activeView === 'chat' ? 'bg-gray-50 text-brand-700' : 'text-gray-700 hover:text-brand-700'
                  }`}
                >
                  <MessageSquarePlus className="w-4 h-4" />
                  <span>New chat</span>
                </button>
                <button 
                  onClick={openFeedbackModal}
                  className="flex items-center space-x-3 w-full px-4 py-3 hover:bg-gray-50 transition-colors text-sm font-medium text-gray-700 hover:text-brand-700"
                >
                  <Send className="w-4 h-4" />
                  <span>Feedback</span>
                </button>
                {accessLevel === 'admin' && (
                  <>
                    <button 
                      onClick={() => handleViewChange('feedback')}
                      className={`flex items-center space-x-3 w-full px-4 py-3 hover:bg-gray-50 transition-colors text-sm font-medium ${
                        activeView === 'feedback' ? 'bg-gray-50 text-brand-700' : 'text-gray-700 hover:text-brand-700'
                      }`}
                    >
                      <FileText className="w-4 h-4" />
                      <span>ReadFeedback</span>
                    </button>
                    <button 
                      onClick={() => handleViewChange('analytics')}
                      className={`flex items-center space-x-3 w-full px-4 py-3 hover:bg-gray-50 transition-colors text-sm font-medium ${
                        activeView === 'analytics' ? 'bg-gray-50 text-brand-700' : 'text-gray-700 hover:text-brand-700'
                      }`}
                    >
                      <BarChart3 className="w-4 h-4" />
                      <span>Analysis</span>
                    </button>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Feedback Modal */}
      <FeedbackModal 
        isOpen={isFeedbackModalOpen}
        onClose={closeFeedbackModal}
        accessLevel={accessLevel}
      />
    </div>
  );
};

export default Header 