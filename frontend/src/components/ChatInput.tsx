import { Send } from 'lucide-react'
import { useRef, useEffect } from 'react'

interface ChatInputProps {
  inputValue: string;
  isLoading: boolean;
  onInputChange: (value: string) => void;
  onSend: () => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ 
  inputValue, 
  isLoading, 
  onInputChange, 
  onSend 
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  const autoResize = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${textarea.scrollHeight}px`;
    }
  };

  useEffect(() => {
    autoResize();
  }, [inputValue]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onInputChange(e.target.value);
    autoResize();
  };

  return (
    <div className="bg-white/95 backdrop-blur-md border-t border-purple-200/50 px-3 sm:px-6 py-4 sm:py-6 shadow-lg">
      <div className="max-w-4xl mx-auto">
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={inputValue}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="Type your message to AF AI in any language..."
            className="w-full resize-none rounded-2xl sm:rounded-3xl bg-white/95 backdrop-blur-md border border-purple-200/60 focus:border-purple-500 focus:ring-2 sm:focus:ring-4 focus:ring-purple-100/50 outline-none px-4 sm:px-6 py-3 sm:py-4 pr-12 sm:pr-16 text-gray-800 placeholder-gray-500 shadow-md transition-all duration-200 font-medium text-sm sm:text-base overflow-hidden"
            rows={1}
            style={{ 
              minHeight: '80px', // Większa wysokość na start dla mobile
              maxHeight: '200px', // Większy max dla lepszego UX
              lineHeight: '1.5',
              fontSize: 'max(16px, 1rem)', // Prevents zoom on iOS
              height: 'auto'
            }}
            disabled={isLoading}
          />
          
          {/* Send Button - positioned inside textarea */}
          <button
            onClick={onSend}
            disabled={!inputValue.trim() || isLoading}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 hover:from-purple-700 hover:via-purple-800 hover:to-violet-900 disabled:from-gray-400 disabled:via-gray-500 disabled:to-gray-600 disabled:cursor-not-allowed rounded-xl sm:rounded-2xl flex items-center justify-center shadow-lg transition-all duration-200 hover:shadow-xl hover:scale-105 active:scale-95"
          >
            <Send className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
          </button>
        </div>
        
        <div className="flex flex-col items-center justify-center mt-4 space-y-2">
          <div className="flex items-center space-x-3">
          <div className="w-2 h-2 bg-purple-300 rounded-full"></div>
          <p className="text-xs text-gray-500 text-center font-medium">
            AF AI can make mistakes. Verify important information in product documentation.
          </p>
          <div className="w-2 h-2 bg-purple-300 rounded-full"></div>
          </div>
                     <div className="flex items-center space-x-2">
             <div className="w-1.5 h-1.5 bg-purple-400 rounded-full"></div>
             <p className="text-xs text-gray-500 text-center font-medium">
               Average response time: 15-40 seconds
             </p>
             <div className="w-1.5 h-1.5 bg-purple-400 rounded-full"></div>
           </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInput 