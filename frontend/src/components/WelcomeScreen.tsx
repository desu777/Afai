import React from 'react'
import { Plus } from 'lucide-react'
import { useImageUpload } from '../hooks/useImageUpload'
import ImagePreview from './ImagePreview'

interface WelcomeScreenProps {
  inputValue: string;
  isLoading: boolean;
  onInputChange: (value: string) => void;
  onSend: () => void;
  selectedImage?: File | null;
  onImageSelect?: (image: File | null) => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  inputValue,
  isLoading,
  onInputChange,
  onSend,
  selectedImage,
  onImageSelect
}) => {
  const textareaRef = React.useRef<HTMLTextAreaElement>(null);
  
  // 🆕 Używam hook do obsługi plików (images + PDFs)
  const { imagePreview, handleImageSelect, removeImage, isPDF, fileType } = useImageUpload({
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

  React.useEffect(() => {
    autoResize();
  }, [inputValue]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onInputChange(e.target.value);
    autoResize();
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] px-4 max-w-4xl mx-auto">
      {/* AF AI Icon */}
      <div className="w-20 h-20 bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 rounded-3xl flex items-center justify-center shadow-2xl mb-6 overflow-hidden">
        <div className="circle">
          <div className="wave"></div>
        </div>
      </div>
      
      {/* Welcome Message */}
      <div className="text-center max-w-md mb-8">
        <h1 className="text-display text-3xl md:text-4xl font-bold text-gray-800 mb-3 tracking-tight">
          Welcome to AF AI
        </h1>
        <p className="text-body text-lg md:text-xl text-gray-600 font-medium leading-relaxed">
          I'm here to make your reef even better.
        </p>
      </div>

      {/* Chat Input */}
      <div className="w-full max-w-3xl">
        {/* 🆕 Podgląd wybranego pliku (image/PDF) */}
        <ImagePreview 
          imagePreview={imagePreview} 
          onRemove={removeImage} 
          isPDF={isPDF}
          fileName={selectedImage?.name}
          fileType={fileType}
          fileSize={selectedImage?.size}
        />
        
        {/* 🆕 Główny kontener - jeden element z textarea + button bar */}
        <div className="relative rounded-2xl sm:rounded-3xl bg-white/95 backdrop-blur-md border border-purple-200/60 focus-within:border-brand-600 focus-within:ring-2 sm:focus-within:ring-4 focus-within:ring-brand-100/50 shadow-md hover:shadow-lg transition-all duration-300 overflow-hidden">
          {/* Textarea */}
          <textarea
            ref={textareaRef}
            value={inputValue}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="Ask me anything about your reef tank in any language..."
            className="w-full resize-none bg-transparent outline-none px-4 sm:px-6 pt-3 sm:pt-4 pb-2 text-gray-800 placeholder-gray-500 font-medium text-sm sm:text-base"
            rows={1}
            style={{ 
              minHeight: '60px',
              maxHeight: '200px',
              lineHeight: '1.5',
              fontSize: 'max(16px, 1rem)',
              height: 'auto'
            }}
            disabled={isLoading}
          />
          
          {/* Button Bar */}
          <div className="flex items-center justify-between px-4 sm:px-6 py-2 sm:py-3 border-t border-purple-100/50">
            {/* Left buttons */}
            <div className="flex items-center space-x-2">
              <label className="w-8 h-8 sm:w-9 sm:h-9 bg-gradient-to-br from-brand-600 via-brand-700 to-brand-800 hover:from-brand-700 hover:via-brand-800 hover:to-brand-900 disabled:from-gray-400 disabled:via-gray-500 disabled:to-gray-600 rounded-xl flex items-center justify-center shadow-brand hover:shadow-brand-lg transition-all duration-300 hover:scale-105 active:scale-95 cursor-pointer">
                <Plus className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
                <input
                  type="file"
                  accept="image/*,application/pdf"
                  onChange={handleImageSelect}
                  className="hidden"
                  disabled={isLoading}
                />
              </label>
              
              {/* ICP button - placeholder */}
              <button 
                className="flex items-center space-x-1 sm:space-x-2 px-3 sm:px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-all duration-200"
                disabled={isLoading}
              >
                <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-sm font-medium hidden sm:inline">ICP</span>
              </button>
              
              {/* Your reef pic button - placeholder */}
              <button 
                className="flex items-center space-x-1 sm:space-x-2 px-3 sm:px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-all duration-200"
                disabled={isLoading}
              >
                <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span className="text-sm font-medium hidden sm:inline">Your reef pic</span>
              </button>
            </div>
            
            {/* Right buttons */}
            <div className="flex items-center">
              <button
                onClick={onSend}
                disabled={!inputValue.trim() || isLoading}
                className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-brand-600 via-brand-700 to-brand-800 hover:from-brand-700 hover:via-brand-800 hover:to-brand-900 disabled:from-gray-400 disabled:via-gray-500 disabled:to-gray-600 disabled:cursor-not-allowed rounded-xl sm:rounded-2xl flex items-center justify-center shadow-brand hover:shadow-brand-lg transition-all duration-300 hover:scale-105 active:scale-95"
              >
                <svg className="w-4 h-4 sm:w-5 sm:h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        {/* Footer note */}
        <div className="text-center mt-6">
          <p className="text-body text-xs text-gray-600 font-medium bg-gray-50/80 rounded-xl px-4 py-2 inline-block border border-gray-200/50 shadow-sm">
            AF AI can make mistakes. Always verify important reef parameters.
          </p>
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen; 