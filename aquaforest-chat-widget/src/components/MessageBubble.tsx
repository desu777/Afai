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