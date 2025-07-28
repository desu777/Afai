import React, { useState, useRef, useEffect } from 'react';
import { Send, FileText, Image } from 'lucide-react';
import { motion } from 'framer-motion';

interface InputFieldProps {
  onSendMessage: (message: string, file?: File) => void;
  disabled?: boolean;
}

export const InputField: React.FC<InputFieldProps> = ({ onSendMessage, disabled = false }) => {
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
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
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
          className="af-file-preview"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          style={{
            padding: '8px 12px',
            background: 'var(--af-gray-100)',
            borderRadius: '8px',
            marginBottom: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {selectedFile.type.startsWith('image/') ? <Image size={16} /> : <FileText size={16} />}
            <span style={{ fontSize: '14px' }}>{selectedFile.name}</span>
          </div>
          <button
            onClick={() => setSelectedFile(null)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '4px',
              color: 'var(--af-gray-600)'
            }}
          >
            ×
          </button>
        </motion.div>
      )}

      <form onSubmit={handleSubmit} className="af-input-wrapper">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about your reef tank..."
          className="af-input-field"
          disabled={disabled}
          rows={1}
        />
        
        <div className="af-input-actions">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,.doc,.docx"
            onChange={(e) => handleFileSelect(e, 'document')}
            style={{ display: 'none' }}
          />
          
          <input
            ref={imageInputRef}
            type="file"
            accept="image/*"
            onChange={(e) => handleFileSelect(e, 'image')}
            style={{ display: 'none' }}
          />

          <button
            type="button"
            className="af-input-button"
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled || !!selectedFile}
            title="Attach document"
          >
            <FileText size={20} />
          </button>

          <button
            type="button"
            className="af-input-button"
            onClick={() => imageInputRef.current?.click()}
            disabled={disabled || !!selectedFile}
            title="Attach image"
          >
            <Image size={20} />
          </button>

          <button
            type="submit"
            className="af-input-button send"
            disabled={disabled || (!message.trim() && !selectedFile)}
          >
            <Send size={20} />
          </button>
        </div>
      </form>
    </div>
  );
};