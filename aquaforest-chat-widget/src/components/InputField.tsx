import React, { useState, useRef, useEffect } from 'react';
import { Send, Plus } from 'lucide-react';
// import { motion } from 'framer-motion';
import { useImageUpload } from '../hooks/useImageUpload';
import { ImagePreview } from './ImagePreview';

interface InputFieldProps {
  onSendMessage: (message: string, file?: File) => void;
  disabled?: boolean;
  onClose?: () => void;
}

export const InputField: React.FC<InputFieldProps> = ({ onSendMessage, disabled = false }) => {
  const [message, setMessage] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  // Use the image upload hook
  const { imagePreview, handleImageSelect, removeImage, isPDF, fileType } = useImageUpload({
    selectedImage: selectedFile,
    onImageSelect: setSelectedFile
  });

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (message.trim() || selectedFile) {
      onSendMessage(message.trim(), selectedFile || undefined);
      setMessage('');
      setSelectedFile(null);
      removeImage();
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const adjustTextareaHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 80)}px`;
    }
  };

  useEffect(() => {
    adjustTextareaHeight();
  }, [message]);


  return (
    <div className="af-input-container">
      {/* Image Preview */}
      <ImagePreview 
        imagePreview={imagePreview} 
        onRemove={removeImage} 
        isPDF={isPDF}
        fileName={selectedFile?.name}
        fileType={fileType}
        fileSize={selectedFile?.size}
      />

      <div className="af-input-main">
        <label 
          className="af-input-attach"
          title="Upload image or PDF"
        >
          <Plus size={20} />
          <input
            type="file"
            accept="image/*,application/pdf"
            onChange={handleImageSelect}
            className="hidden"
            disabled={disabled || !!selectedFile}
          />
        </label>
        
        <div className="af-input-field-wrapper">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            className="af-input-field"
            disabled={disabled}
            rows={1}
          />
        </div>

        <button
          type="button"
          className="af-input-send"
          disabled={disabled || (!message.trim() && !selectedFile)}
          onClick={handleSubmit}
        >
          <Send size={20} />
        </button>
      </div>

      <div className="af-input-footer">
        Afai can make mistakes. Always verify important information.
      </div>
    </div>
  );
};