import React from 'react'
import { Plus } from 'lucide-react'
import { useImageUpload } from '../hooks/useImageUpload'
import ImagePreview from './ImagePreview'
import { ResponseFormat } from '../types'

interface WelcomeScreenProps {
  inputValue: string;
  isLoading: boolean;
  onInputChange: (value: string) => void;
  onSend: () => void;
  selectedImage?: File | null;
  onImageSelect?: (image: File | null) => void;
  responseFormat?: ResponseFormat;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({
  inputValue,
  isLoading,
  onInputChange,
  onSend,
  selectedImage,
  onImageSelect,
  responseFormat
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
      <div className="w-20 h-20 bg-brand-600 rounded-2xl flex items-center justify-center shadow-lg mb-6 overflow-hidden">
        <div className="circle">
          <div className="wave"></div>
        </div>
      </div>
      
      {/* Welcome Message */}
      <div className="text-center max-w-md mb-8">
        <h1 className="text-display text-3xl md:text-4xl font-bold text-gray-800 mb-3 tracking-tight">
          {responseFormat === 'ghostwriter' ? 'AF Support Ghostwriter' : 'Meet Afai'}
        </h1>
        <p className="text-body text-lg md:text-xl text-gray-600 font-medium leading-relaxed">
          {responseFormat === 'ghostwriter' 
            ? 'Helping you respond to community messages' 
            : 'Wisdom from the reef\'s heart...'}
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
        <div className="relative rounded-2xl bg-white border border-gray-200 focus-within:border-brand-600 focus-within:ring-2 focus-within:ring-brand-600/20 shadow-sm hover:shadow-md transition-shadow duration-200 overflow-hidden">
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
          <div className="flex items-center justify-between px-4 sm:px-6 py-2 sm:py-3 border-t border-gray-100">
            {/* Left buttons */}
            <div className="flex items-center space-x-2">
              <label className="w-8 h-8 sm:w-9 sm:h-9 bg-brand-600 hover:bg-brand-700 disabled:bg-gray-400 rounded-xl flex items-center justify-center shadow-sm transition-colors duration-200 cursor-pointer">
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
                className="flex items-center space-x-1 sm:space-x-2 px-3 sm:px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-xl transition-all duration-200"
                disabled={isLoading}
              >
                <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span className="text-sm font-medium hidden sm:inline">ICP</span>
              </button>
              
              {/* Your reef pic button - placeholder */}
              <button 
                className="flex items-center space-x-1 sm:space-x-2 px-3 sm:px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-xl transition-all duration-200"
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
                className="w-8 h-8 sm:w-10 sm:h-10 bg-brand-600 hover:bg-brand-700 disabled:bg-gray-400 disabled:cursor-not-allowed rounded-xl flex items-center justify-center shadow-sm transition-colors duration-200"
              >
                <svg className="w-4 h-4 sm:w-5 sm:h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        {/* Footer with Logo */}
        <div className="text-center mt-8 space-y-4">
          <img 
            src="/aquaforest_logo.png" 
            alt="Aquaforest" 
            className="h-8 mx-auto opacity-60 hover:opacity-80 transition-opacity"
          />
          <p className="text-body text-xs text-gray-500 font-medium">
            Afai can make mistakes. Always verify important reef parameters.
          </p>
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen; 