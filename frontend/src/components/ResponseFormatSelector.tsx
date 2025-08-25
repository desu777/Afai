import { useState, useEffect, useRef } from 'react'
import { ChevronDown, Sparkles, PenTool, Brain } from 'lucide-react'
import { ResponseFormat, ResponseFormatOption } from '../types'

interface ResponseFormatSelectorProps {
  selectedFormat: ResponseFormat;
  onFormatChange: (format: ResponseFormat) => void;
  accessLevel: 'visionary_expert' | 'admin';
}

const formatOptions: ResponseFormatOption[] = [
  {
    id: 'visionary_expert',
    label: 'Visionary Expert',
    description: 'Enthusiastic AI assistant with passion for reefing'
  },
  {
    id: 'ghostwriter',
    label: 'Ghostwriter',
    description: 'Professional support team responses for forums'
  },
  {
    id: 'new_mode',
    label: 'New Mode',
    description: 'Advanced diagnostic system with user-level adaptation'
  }
];

const ResponseFormatSelector: React.FC<ResponseFormatSelectorProps> = ({
  selectedFormat,
  onFormatChange,
  accessLevel
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Filter options based on access level
  const availableOptions = formatOptions.filter(option => {
    if (accessLevel === 'admin') {
      return true; // Admin sees all options
    } else {
      return option.id !== 'ghostwriter'; // Visionary expert doesn't see ghostwriter
    }
  });

  const selectedOption = availableOptions.find(option => option.id === selectedFormat) || availableOptions[0];

  const closeDropdown = () => {
    setIsClosing(true);
    setTimeout(() => {
      setIsOpen(false);
      setIsClosing(false);
    }, 150);
  };

  const handleOptionSelect = (format: ResponseFormat) => {
    onFormatChange(format);
    closeDropdown();
  };

  const getOptionIcon = (formatId: ResponseFormat) => {
    switch (formatId) {
      case 'visionary_expert':
        return <Sparkles className="w-4 h-4" />;
      case 'ghostwriter':
        return <PenTool className="w-4 h-4" />;
      case 'new_mode':
        return <Brain className="w-4 h-4" />;
      default:
        return <Sparkles className="w-4 h-4" />;
    }
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        closeDropdown();
      }
    };

    if (isOpen && !isClosing) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, isClosing]);

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Selector Button */}
      <button
        onClick={() => {
          if (isOpen) {
            closeDropdown();
          } else {
            setIsOpen(true);
          }
        }}
        className={`
          inline-flex items-center justify-between min-w-[200px] px-4 py-2.5 
          bg-white/95 backdrop-blur-md border border-purple-200/50 rounded-xl 
          shadow-sm hover:shadow-md hover:border-purple-300/60 
          transition-all duration-200 hover:scale-[1.02] active:scale-98
          text-sm font-medium text-gray-700 hover:text-brand-700
          ${isOpen ? 'ring-2 ring-purple-200/50 border-purple-300/60' : ''}
        `}
      >
        <div className="flex items-center space-x-2.5">
          {getOptionIcon(selectedOption.id)}
          <span className="truncate">{selectedOption.label}</span>
        </div>
        <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${
          isOpen ? 'rotate-180' : ''
        }`} />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className={`
          absolute top-full left-0 mt-2 w-full min-w-[280px] z-50
          bg-white/95 backdrop-blur-md border border-purple-200/50 rounded-xl 
          shadow-xl overflow-hidden
          ${isClosing ? 'animate-dropdown-out' : 'animate-dropdown-in'}
        `}>
          <div className="py-2">
            {availableOptions.map((option) => (
              <button
                key={option.id}
                onClick={() => handleOptionSelect(option.id)}
                className={`
                  flex items-start space-x-3 w-full px-4 py-3 text-left
                  hover:bg-purple-50/80 transition-colors duration-150
                  ${option.id === selectedFormat 
                    ? 'bg-purple-50/80 text-brand-700 border-r-2 border-purple-400' 
                    : 'text-gray-700 hover:text-brand-700'
                  }
                `}
              >
                <div className="flex-shrink-0 mt-0.5">
                  {getOptionIcon(option.id)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2">
                    <span className="font-medium text-sm">{option.label}</span>
                    {option.id === selectedFormat && (
                      <div className="w-1.5 h-1.5 bg-brand-500 rounded-full"></div>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">
                    {option.description}
                  </p>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResponseFormatSelector;