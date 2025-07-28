import React from 'react';
import { motion } from 'framer-motion';
import { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.type === 'user';

  return (
    <motion.div
      className={`af-message ${isUser ? 'user' : 'assistant'}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {!isUser && (
        <div className="af-message-avatar">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none">
            <path
              d="M5 12C5 16.97 8.03 21 12 21C12.45 21 12.89 20.96 13.32 20.88C13.12 20.46 13 20 13 19.5C13 18.12 14.12 17 15.5 17C16.34 17 17.08 17.43 17.5 18.1C19.04 16.8 20 14.97 20 12.9C20 10.32 18.82 8.03 17 6.63C16.94 5.17 15.74 4 14.27 4C13.33 4 12.53 4.59 12.2 5.41C8.84 5.86 6.24 8.24 5.28 11.35C5.1 11.55 5 11.77 5 12Z"
              fill="currentColor"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
      )}
      <div className="af-message-bubble">
        {message.content}
        
        {message.fileName && (
          <div style={{
            marginTop: '8px',
            fontSize: '12px',
            opacity: 0.8,
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}>
            📎 {message.fileName}
          </div>
        )}
      </div>
    </motion.div>
  );
};