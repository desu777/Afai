import React from 'react';
import { motion } from 'framer-motion';
import { Copy, Download, CheckCircle } from 'lucide-react';
import { Message } from '../types';
import { MessageContent } from './MessageContent';
import { TruncatedMessageContent } from './TruncatedMessageContent';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.type === 'user';

  // Function to generate professional attachment message
  const getAttachmentMessage = (message: Message): string => {
    const isImage = message.fileType === 'image';
    const prefix = isImage ? 'Image Added:' : 'File Added:';
    return `✓ *${prefix}* ${message.fileName}`;
  };

  // Function to copy message content
  const handleCopy = async () => {
    try {
      // Clean markdown formatting
      const cleanContent = message.content
        .replace(/\[SHOW_MORE_START\](.*?)\[SHOW_MORE_END\]/gs, '$1')
        .replace(/^####\s+(.+)$/gm, '\n$1\n')
        .replace(/^###\s+(.+)$/gm, '\n$1\n')
        .replace(/^##\s+(.+)$/gm, '\n$1\n')
        .replace(/^#\s+(.+)$/gm, '\n$1\n')
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '$1 ($2)')
        .replace(/^\*\s+(.+)$/gm, '• $1')
        .replace(/\*\*(.*?)\*\*/g, '$1')
        .replace(/^---$/gm, '')
        .replace(/\n\s*\n\s*\n/g, '\n\n')
        .trim();
      
      await navigator.clipboard.writeText(cleanContent);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  // Function to download message as PDF
  const handleDownloadPDF = async () => {
    try {
      const printWindow = window.open('', '_blank');
      if (!printWindow) return;

      let htmlContent = message.content
        .replace(/\[SHOW_MORE_START\](.*?)\[SHOW_MORE_END\]/gs, '$1')
        .replace(/^####\s+(.+)$/gm, '<h4>$1</h4>')
        .replace(/^###\s+(.+)$/gm, '<h3>$1</h3>')
        .replace(/^##\s+(.+)$/gm, '<h2>$1</h2>')
        .replace(/^#\s+(.+)$/gm, '<h1>$1</h1>')
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '$1 ($2)')
        .replace(/^\*\s+(.+)$/gm, '• $1')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/^• (.+)$/gm, '<li>$1</li>')
        .replace(/^---$/gm, '<hr>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');

      htmlContent = htmlContent.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
      htmlContent = '<p>' + htmlContent + '</p>';
      htmlContent = htmlContent.replace(/<p><\/p>/g, '');

      const fullHtmlContent = `
        <html>
          <head>
            <title>Afai Response - ${new Date().toLocaleDateString()}</title>
            <style>
              body { 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                line-height: 1.6; 
                color: #333;
              }
              h1, h2, h3 { color: #47154C; margin-top: 20px; }
              .header { 
                border-bottom: 2px solid #47154C; 
                padding-bottom: 10px; 
                margin-bottom: 20px; 
              }
              .header a {
                color: #47154C;
                text-decoration: none;
                font-weight: bold;
              }
              .header a:after {
                content: " ↗";
                font-size: 0.8em;
                opacity: 0.7;
              }
              .timestamp { color: #666; font-size: 12px; }
              strong { color: #333; font-weight: bold; }
              ul { margin: 10px 0; padding-left: 20px; }
              li { margin: 5px 0; }
              hr { border: none; border-top: 1px solid #ccc; margin: 20px 0; }
            </style>
          </head>
          <body>
            <div class="header">
              <h1>Afai Response - Reef Expert made by <a href="https://aquaforest.eu/">Aquaforest</a></h1>
              <div class="timestamp">Generated: ${message.timestamp.toLocaleString()}</div>
            </div>
            <div>${htmlContent}</div>
          </body>
        </html>
      `;

      printWindow.document.write(fullHtmlContent);
      printWindow.document.close();
      
      setTimeout(() => {
        printWindow.print();
        printWindow.close();
      }, 250);
    } catch (err) {
      console.error('Failed to generate PDF: ', err);
    }
  };

  return (
    <motion.div
      className={`af-message ${isUser ? 'user' : 'assistant'}`}
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="af-message-wrapper">
        <div className="af-message-bubble">
          
          {isUser ? (
            <MessageContent 
              content={message.fileName ? 
                `${message.content}\n\n${getAttachmentMessage(message)}` : 
                message.content
              } 
              isUser={true} 
            />
          ) : (
            <TruncatedMessageContent content={message.content} isUser={false} />
          )}
        </div>
        
        <div className="af-message-footer">
          <span className="af-message-time">
            {message.timestamp.toLocaleTimeString('en-US', { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </span>
          
          {!isUser && (
            <div className="af-message-actions">
              <button
                onClick={handleCopy}
                className="af-message-action"
                title="Copy response"
              >
                <Copy size={14} />
              </button>
              <button
                onClick={handleDownloadPDF}
                className="af-message-action"
                title="Download as PDF"
              >
                <Download size={14} />
              </button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};