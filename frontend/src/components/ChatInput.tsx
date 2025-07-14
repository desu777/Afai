import { Send, Camera, FileText } from 'lucide-react'
import { useRef, useEffect } from 'react'
import { useImageUpload } from '../hooks/useImageUpload'
import ImagePreview from './ImagePreview'

interface ChatInputProps {
  inputValue: string;
  isLoading: boolean;
  onInputChange: (value: string) => void;
  onSend: () => void;
  hasMessages?: boolean;
  selectedImage?: File | null;
  onImageSelect?: (image: File | null) => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ 
  inputValue, 
  isLoading, 
  onInputChange, 
  onSend,
  hasMessages = false,
  selectedImage,
  onImageSelect
}) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  // 🆕 Używam hook do obsługi plików (images + PDFs)
  const { imagePreview, handleImageSelect, removeImage, isPDF, isImage, fileType } = useImageUpload({
    selectedImage,
    onImageSelect
  });
  
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
    <div className="px-3 sm:px-6 py-4 sm:py-6">
      <div className={hasMessages ? "max-w-4xl mx-auto" : "mx-auto"}>
        {/* 🆕 Podgląd wybranego pliku (image/PDF) */}
        <ImagePreview 
          imagePreview={imagePreview} 
          onRemove={removeImage} 
          isPDF={isPDF}
          fileName={selectedImage?.name}
          fileType={fileType}
        />
        
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
              minHeight: '80px',
              maxHeight: '200px',
              lineHeight: '1.5',
              fontSize: 'max(16px, 1rem)',
              height: 'auto'
            }}
            disabled={isLoading}
          />
          
          <button
            onClick={onSend}
            disabled={!inputValue.trim() || isLoading}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 hover:from-purple-700 hover:via-purple-800 hover:to-violet-900 disabled:from-gray-400 disabled:via-gray-500 disabled:to-gray-600 disabled:cursor-not-allowed rounded-xl sm:rounded-2xl flex items-center justify-center shadow-lg transition-all duration-200 hover:shadow-xl hover:scale-105 active:scale-95"
          >
            <Send className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
          </button>
          
          {/* 🆕 Przycisk wyboru pliku (image/PDF) */}
          <label className="absolute right-12 sm:right-14 top-1/2 transform -translate-y-1/2 w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 hover:from-purple-700 hover:via-purple-800 hover:to-violet-900 disabled:from-gray-400 disabled:via-gray-500 disabled:to-gray-600 rounded-xl sm:rounded-2xl flex items-center justify-center shadow-lg transition-all duration-200 hover:shadow-xl hover:scale-105 active:scale-95 cursor-pointer" title="Upload image or PDF">
            {selectedImage && isPDF ? (
              <FileText className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            ) : (
              <Camera className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            )}
            <input
              type="file"
              accept="image/*,application/pdf"
              onChange={handleImageSelect}
              className="hidden"
              disabled={isLoading}
            />
          </label>
        </div>
        
        {/* Footer note - only show when no messages */}
        {!hasMessages && (
          <div className="text-center mt-4 space-y-2">
            <p className="text-xs text-gray-500 font-medium">
              AF AI can make mistakes. Check important data.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInput 