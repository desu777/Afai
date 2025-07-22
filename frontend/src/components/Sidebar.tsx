import { useState, useEffect, useRef } from 'react'
import { 
  MessageSquarePlus, 
  Send, 
  FileText, 
  BarChart3, 
  Menu, 
  X,
  ChevronLeft,
  ChevronRight,
  HelpCircle,
  History,
  LogOut,
  Shield,
  Headphones,
  User
} from 'lucide-react'
import FeedbackModal from './FeedbackModal'
import RelogConfirmModal from './RelogConfirmModal'

interface SidebarProps {
  accessLevel: 'test' | 'admin' | 'support';
  onViewChange?: (view: 'chat' | 'feedback' | 'analytics' | 'examples' | 'updates') => void;
  activeView?: 'chat' | 'feedback' | 'analytics' | 'examples' | 'updates';
  isCollapsed?: boolean;
  onToggleCollapse?: (collapsed: boolean) => void;
  onRelog?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ 
  accessLevel, 
  onViewChange, 
  activeView = 'chat',
  isCollapsed = false,
  onToggleCollapse,
  onRelog
}) => {
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const [isFeedbackModalOpen, setIsFeedbackModalOpen] = useState(false);
  const [isRelogModalOpen, setIsRelogModalOpen] = useState(false);
  const sidebarRef = useRef<HTMLDivElement>(null);

  const openFeedbackModal = () => {
    setIsFeedbackModalOpen(true);
    setIsMobileOpen(false);
  };

  const closeFeedbackModal = () => {
    setIsFeedbackModalOpen(false);
  };

  const openRelogModal = () => {
    setIsRelogModalOpen(true);
    setIsMobileOpen(false);
  };

  const closeRelogModal = () => {
    setIsRelogModalOpen(false);
  };

  const handleRelogConfirm = () => {
    setIsRelogModalOpen(false);
    onRelog?.();
  };

  const handleViewChange = (view: 'chat' | 'feedback' | 'analytics' | 'examples' | 'updates') => {
    onViewChange?.(view);
    setIsMobileOpen(false);
  };

  const toggleMobileMenu = () => {
    setIsMobileOpen(!isMobileOpen);
  };

  const toggleCollapse = () => {
    onToggleCollapse?.(!isCollapsed);
  };

  // Close mobile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (sidebarRef.current && !sidebarRef.current.contains(event.target as Node)) {
        setIsMobileOpen(false);
      }
    };

    if (isMobileOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isMobileOpen]);

  const getUserBadgeInfo = () => {
    switch (accessLevel) {
      case 'admin':
        return {
          label: 'Admin',
          icon: Shield,
          bgClass: 'bg-purple-100 text-purple-700 border-purple-200',
          iconBgClass: 'bg-purple-600'
        };
      case 'support':
        return {
          label: 'Support',
          icon: Headphones,
          bgClass: 'bg-blue-100 text-blue-700 border-blue-200',
          iconBgClass: 'bg-blue-600'
        };
      case 'test':
      default:
        return {
          label: 'Tester',
          icon: User,
          bgClass: 'bg-green-100 text-green-700 border-green-200',
          iconBgClass: 'bg-green-600'
        };
    }
  };

  const getButtonClass = (_view: 'chat' | 'feedback' | 'analytics' | 'examples' | 'updates', isActive: boolean) => {
    if (isCollapsed) {
      const baseClassCollapsed = "flex items-center justify-center w-10 h-10 rounded-xl transition-all duration-300 hover:bg-brand-50 hover:shadow-brand text-sm font-medium group mx-auto transform hover:scale-105 active:scale-95";
      const activeClassCollapsed = "bg-brand-100 text-brand-700 border border-brand-200/50 shadow-brand";
      const inactiveClassCollapsed = "text-gray-700 hover:text-brand-700 hover:bg-brand-50";
      
      return `${baseClassCollapsed} ${isActive ? activeClassCollapsed : inactiveClassCollapsed}`;
    }
    
    const baseClass = "flex items-center space-x-3 w-full px-4 py-3 rounded-xl transition-all duration-300 hover:bg-brand-50 hover:shadow-brand text-sm font-medium group transform hover:scale-[1.02] active:scale-[0.98]";
    const activeClass = "bg-brand-100 text-brand-700 border border-brand-200/50 shadow-brand";
    const inactiveClass = "text-gray-700 hover:text-brand-700 hover:bg-brand-50";
    
    return `${baseClass} ${isActive ? activeClass : inactiveClass}`;
  };

  return (
    <>
      {/* Mobile Menu Button - Fixed position - ukryty gdy sidebar otwarty */}
      {!isMobileOpen && (
        <button
          onClick={toggleMobileMenu}
          className="md:hidden fixed top-4 left-4 z-50 p-2 bg-white/95 backdrop-blur-md rounded-xl shadow-lg border border-purple-200/50 hover:bg-purple-50 transition-all duration-200"
        >
          <Menu className="w-5 h-5 text-gray-700" />
        </button>
      )}

      {/* Mobile Overlay */}
      {isMobileOpen && (
        <div className="md:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-40" onClick={() => setIsMobileOpen(false)} />
      )}

      {/* Sidebar */}
      <div 
        ref={sidebarRef}
        className={`
          fixed md:relative top-0 left-0 h-full bg-white/95 backdrop-blur-md border-r border-purple-200/50 shadow-lg z-40
          transition-all duration-300 ease-in-out
          ${isMobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
          ${isCollapsed ? 'md:w-16' : 'w-80 md:w-80'}
        `}
      >
        <div className="flex flex-col h-full">
          {/* Header Section */}
          <div className="flex items-center justify-between p-4 md:p-6 border-b border-purple-200/30">
            {!isCollapsed && (
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 md:w-14 md:h-14 bg-gradient-to-br from-brand-600 via-brand-700 to-brand-800 rounded-xl flex items-center justify-center shadow-brand overflow-hidden">
                  <img 
                    src="/horse.png" 
                    alt="Konik morski" 
                    className="w-7 h-7 md:w-8 md:h-8 object-contain"
                  />
                </div>
                <div className="flex flex-col">
                  <div className="h-8 md:h-10">
                    <svg viewBox="0 0 140 30" className="w-full h-full max-w-[200px] md:max-w-[240px]">
                      <defs>
                        <linearGradient id="sidebar-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                          <stop offset="0%" style={{stopColor: '#9333ea'}} />
                          <stop offset="50%" style={{stopColor: '#7c3aed'}} />
                          <stop offset="100%" style={{stopColor: '#5b21b6'}} />
                        </linearGradient>
                        <pattern id="sidebar-wave" x="0" y="-0.5" width="100%" height="100%" patternUnits="userSpaceOnUse">
                          <path d="M-40 15 Q-30 12 -20 15 T0 15 T20 15 T40 15 T60 15 T80 15 T100 15 T120 15 T140 15 T160 15 V30 H-40z" fill="url(#sidebar-gradient)">
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
                      <text textAnchor="middle" x="70" y="21" fontSize="18" fontWeight="bold" fill="#1f2937" fillOpacity="0.15" fontFamily="Poppins">AF AI Assistant</text>
                      <text textAnchor="middle" x="70" y="21" fontSize="18" fontWeight="bold" fill="url(#sidebar-wave)" fillOpacity="1" fontFamily="Poppins">AF AI Assistant</text>
                    </svg>
                  </div>
                </div>
              </div>
            )}
            
            {/* Close button for mobile */}
            <button
              onClick={() => setIsMobileOpen(false)}
              className="md:hidden p-2 hover:bg-purple-100 rounded-lg transition-colors"
            >
              <X className="w-5 h-5 text-gray-600" />
            </button>

            {/* Collapse button for desktop */}
            <button
              onClick={toggleCollapse}
              className="hidden md:block p-2 hover:bg-purple-100 rounded-lg transition-colors"
            >
              {isCollapsed ? (
                <ChevronRight className="w-4 h-4 text-gray-600" />
              ) : (
                <ChevronLeft className="w-4 h-4 text-gray-600" />
              )}
            </button>
          </div>

          {/* Navigation Menu */}
          <div className="flex-1 px-4 py-6 space-y-2">
            {/* New Chat Button */}
            <button 
              onClick={() => handleViewChange('chat')}
              className={getButtonClass('chat', activeView === 'chat')}
              title={isCollapsed ? 'New chat' : ''}
            >
              <MessageSquarePlus className="w-5 h-5 flex-shrink-0" />
              {!isCollapsed && <span>New chat</span>}
            </button>

            {/* Feedback Button */}
            <button 
              onClick={openFeedbackModal}
              className={
                isCollapsed 
                  ? "flex items-center justify-center w-10 h-10 rounded-xl transition-all duration-300 hover:bg-brand-50 hover:shadow-brand text-sm font-medium text-gray-700 hover:text-brand-700 mx-auto transform hover:scale-105 active:scale-95"
                  : "flex items-center space-x-3 w-full px-4 py-3 rounded-xl transition-all duration-300 hover:bg-brand-50 hover:shadow-brand text-sm font-medium text-gray-700 hover:text-brand-700 transform hover:scale-[1.02] active:scale-[0.98]"
              }
              title={isCollapsed ? 'Feedback' : ''}
            >
              <Send className="w-5 h-5 flex-shrink-0" />
              {!isCollapsed && <span>Feedback</span>}
            </button>

            {/* Admin Only Buttons */}
            {accessLevel === 'admin' && (
              <>
                <button 
                  onClick={() => handleViewChange('feedback')}
                  className={getButtonClass('feedback', activeView === 'feedback')}
                  title={isCollapsed ? 'Read Feedback' : ''}
                >
                  <FileText className="w-5 h-5 flex-shrink-0" />
                  {!isCollapsed && <span>Read Feedback</span>}
                </button>
                
                <button 
                  onClick={() => handleViewChange('analytics')}
                  className={getButtonClass('analytics', activeView === 'analytics')}
                  title={isCollapsed ? 'Analytics' : ''}
                >
                  <BarChart3 className="w-5 h-5 flex-shrink-0" />
                  {!isCollapsed && <span>Analytics</span>}
                </button>
              </>
            )}

            {/* Examples Button - available for all users */}
            <button 
              onClick={() => handleViewChange('examples')}
              className={getButtonClass('examples', activeView === 'examples')}
              title={isCollapsed ? 'Examples' : ''}
            >
              <HelpCircle className="w-5 h-5 flex-shrink-0" />
              {!isCollapsed && <span>Examples</span>}
            </button>

            {/* Updates Button - available for all users */}
            <button 
              onClick={() => handleViewChange('updates')}
              className={getButtonClass('updates', activeView === 'updates')}
              title={isCollapsed ? 'Updates' : ''}
            >
              <History className="w-5 h-5 flex-shrink-0" />
              {!isCollapsed && <span>Updates</span>}
            </button>

            {/* Relog Button - available for all users */}
            <button 
              onClick={openRelogModal}
              className={
                isCollapsed 
                  ? "flex items-center justify-center w-10 h-10 rounded-xl transition-all duration-300 hover:bg-red-50 hover:shadow-md text-sm font-medium text-gray-700 hover:text-red-700 mx-auto transform hover:scale-105 active:scale-95"
                  : "flex items-center space-x-3 w-full px-4 py-3 rounded-xl transition-all duration-300 hover:bg-red-50 hover:shadow-md text-sm font-medium text-gray-700 hover:text-red-700 transform hover:scale-[1.02] active:scale-[0.98]"
              }
              title={isCollapsed ? 'Logout' : ''}
            >
              <LogOut className="w-5 h-5 flex-shrink-0" />
              {!isCollapsed && <span>Logout</span>}
            </button>
          </div>

          {/* Footer Info Section */}
          {!isCollapsed && (
            <div className="border-t border-purple-200/30 px-4 py-6 space-y-4">
              {/* User Status Badge */}
              <div className="flex justify-center">
                {(() => {
                  const userInfo = getUserBadgeInfo();
                  const IconComponent = userInfo.icon;
                  
                  let badgeClasses = '';
                  switch (accessLevel) {
                    case 'admin':
                      badgeClasses = 'bg-purple-100/80 text-purple-700 border-purple-200/50';
                      break;
                    case 'support':
                      badgeClasses = 'bg-blue-100/80 text-blue-700 border-blue-200/50';
                      break;
                    case 'test':
                    default:
                      badgeClasses = 'bg-green-100/80 text-green-700 border-green-200/50';
                      break;
                  }
                  
                  return (
                    <div className={`inline-flex items-center space-x-2 ${badgeClasses} backdrop-blur-md rounded-full px-3 py-1 shadow-sm border`}>
                      <IconComponent className="w-3 h-3" />
                      <span className="text-xs font-semibold">Logged as: {userInfo.label}</span>
                    </div>
                  );
                })()}
              </div>

              {/* Version Badge */}
              <div className="flex justify-center">
                <div className="inline-block bg-purple-100/80 backdrop-blur-md rounded-full px-3 py-1 shadow-sm border border-purple-200/50">
                  <span className="text-xs font-semibold text-purple-700">Current version: 2.1</span>
                </div>
              </div>

              {/* Disclaimer */}
              <div className="space-y-3 text-center">
                <p className="text-xs text-gray-600 font-medium leading-relaxed bg-gray-50/60 rounded-lg px-3 py-2 border border-gray-200/40">
                  AF AI can make mistakes. Always verify important information in product documentation.
                </p>
                
                <p className="text-xs text-gray-600 font-medium bg-blue-50/60 rounded-lg px-3 py-2 border border-blue-200/40">
                  Average response time: 15-40 seconds
                </p>
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

      {/* Relog Confirmation Modal */}
      <RelogConfirmModal 
        isOpen={isRelogModalOpen}
        onClose={closeRelogModal}
        onConfirm={handleRelogConfirm}
      />
    </>
  );
};

export default Sidebar; 