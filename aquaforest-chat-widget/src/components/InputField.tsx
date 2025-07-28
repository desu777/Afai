import React, { useState, useRef, useEffect } from 'react';
import { Send, FileText, Camera, X } from 'lucide-react';
import { motion } from 'framer-motion';

interface InputFieldProps {
  onSendMessage: (message: string, file?: File) => void;
  disabled?: boolean;
  onClose?: () => void;
}

export const InputField: React.FC<InputFieldProps> = ({ onSendMessage, disabled = false, onClose }) => {
  const [message, setMessage] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (message.trim() || selectedFile) {
      onSendMessage(message.trim(), selectedFile || undefined);
      setMessage('');
      setSelectedFile(null);
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

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>, type: 'document' | 'image') => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
    // Reset input
    e.target.value = '';
  };

  return (
    <div className="af-input-container">
      {selectedFile && (
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            padding: '8px 12px',
            background: 'rgba(255, 255, 255, 0.1)',
            margin: '0 12px 8px',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'white' }}>
            {selectedFile.type.startsWith('image/') ? <Camera size={16} /> : <FileText size={16} />}
            <span style={{ fontSize: '14px' }}>{selectedFile.name}</span>
          </div>
          <button
            onClick={() => setSelectedFile(null)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '4px',
              color: 'white'
            }}
          >
            ×
          </button>
        </motion.div>
      )}

      <div className="af-input-top-bar">
        <button type="button" className="af-input-close" onClick={onClose}>
          <X size={24} />
        </button>
        
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
          onClick={handleSubmit}
          className="af-input-ok"
          disabled={disabled || (!message.trim() && !selectedFile)}
        >
          OK
        </button>
      </div>

      <div className="af-input-bottom-bar">
        <input
          ref={imageInputRef}
          type="file"
          accept="image/*"
          onChange={(e) => handleFileSelect(e, 'image')}
          style={{ display: 'none' }}
        />
        
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.doc,.docx"
          onChange={(e) => handleFileSelect(e, 'document')}
          style={{ display: 'none' }}
        />

        <button
          type="button"
          className="af-input-icon-button"
          onClick={() => imageInputRef.current?.click()}
          disabled={disabled || !!selectedFile}
          title="Attach image"
        >
          <Camera size={24} />
        </button>

        <span className="af-input-center-text">Message</span>

        <button
          type="button"
          className="af-input-icon-button"
          disabled={disabled || !message.trim()}
          onClick={handleSubmit}
        >
          <Send size={24} />
        </button>
      </div>
    </div>
  );
};