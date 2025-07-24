import { User, Copy, Download } from 'lucide-react'
import { Message as MessageType } from '../types'
import MessageContent from './MessageContent'
import TruncatedMessageContent from './TruncatedMessageContent'
import MessageFileDisplay from './MessageFileDisplay'

interface MessageProps {
  message: MessageType;
}

const Message: React.FC<MessageProps> = ({ message }) => {
  // Function to copy message content as clean text without markdown formatting
  const handleCopy = async () => {
    try {
      // Clean markdown formatting and convert links to full URLs
      let cleanContent = message.content
        // Remove collapsible section markers and extract content
        .replace(/\[SHOW_MORE_START\](.*?)\[SHOW_MORE_END\]/gs, '$1')
        // Clean markdown headers (remove # symbols and add spacing)
        .replace(/^####\s+(.+)$/gm, '\n$1\n')
        .replace(/^###\s+(.+)$/gm, '\n$1\n')
        .replace(/^##\s+(.+)$/gm, '\n$1\n')
        .replace(/^#\s+(.+)$/gm, '\n$1\n')
        // Convert markdown links to full URLs
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '$1 ($2)')
        // Convert markdown asterisk lists to bullet points
        .replace(/^\*\s+(.+)$/gm, '• $1')
        // Remove bold formatting
        .replace(/\*\*(.*?)\*\*/g, '$1')
        // Remove horizontal rules
        .replace(/^---$/gm, '')
        // Clean up extra whitespace/empty lines
        .replace(/\n\s*\n\s*\n/g, '\n\n')
        .trim();
      
      await navigator.clipboard.writeText(cleanContent);
      
      // Optional: Show a brief success indicator
      // You could add a toast notification here
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  // Function to download message as PDF with formatted content
  const handleDownloadPDF = async () => {
    try {
      // Create a new window with the content
      const printWindow = window.open('', '_blank');
      if (!printWindow) return;

      // Convert markdown to HTML for better PDF formatting
      let htmlContent = message.content
        // Remove collapsible section markers and extract content
        .replace(/\[SHOW_MORE_START\](.*?)\[SHOW_MORE_END\]/gs, '$1')
        // Convert markdown headers to HTML
        .replace(/^####\s+(.+)$/gm, '<h4>$1</h4>')
        .replace(/^###\s+(.+)$/gm, '<h3>$1</h3>')
        .replace(/^##\s+(.+)$/gm, '<h2>$1</h2>')
        .replace(/^#\s+(.+)$/gm, '<h1>$1</h1>')
        // Convert markdown links to full URLs
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '$1 ($2)')
        // Convert markdown asterisk lists to bullet points
        .replace(/^\*\s+(.+)$/gm, '• $1')
        // Convert bold text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Convert bullet points to HTML list items
        .replace(/^• (.+)$/gm, '<li>$1</li>')
        // Convert horizontal rules
        .replace(/^---$/gm, '<hr>')
        // Convert paragraphs (double line breaks)
        .replace(/\n\n/g, '</p><p>')
        // Single line breaks
        .replace(/\n/g, '<br>');

      // Wrap list items in ul tags
      htmlContent = htmlContent.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');
      
      // Wrap in paragraphs
      htmlContent = '<p>' + htmlContent + '</p>';
      
      // Clean up empty paragraphs
      htmlContent = htmlContent.replace(/<p><\/p>/g, '');

      // Basic HTML structure for PDF
      const fullHtmlContent = `
        <html>
          <head>
            <title>Afai Response - Reef Expert made by Aquaforest - ${new Date().toLocaleDateString()}</title>
            <style>
              body { 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                line-height: 1.6; 
                color: #333;
              }
              h1, h2, h3 { color: #7c3aed; margin-top: 20px; }
                             .header { 
                 border-bottom: 2px solid #7c3aed; 
                 padding-bottom: 10px; 
                 margin-bottom: 20px; 
               }
               .header a {
                 color: #7c3aed;
                 text-decoration: none;
                 font-weight: bold;
               }
               .header a:after {
                 content: " ↗";
                 font-size: 0.8em;
                 opacity: 0.7;
               }
              .timestamp { color: #666; font-size: 12px; }
              .content { 
                font-size: 14px;
                line-height: 1.6;
              }
              strong { color: #333; font-weight: bold; }
              ul { margin: 10px 0; padding-left: 20px; }
              li { margin: 5px 0; }
              hr { 
                border: none; 
                border-top: 1px solid #ccc; 
                margin: 20px 0; 
              }
              p { margin: 10px 0; }
            </style>
          </head>
          <body>
                         <div class="header">
               <h1>Afai Response - Reef Expert made by <a href="https://aquaforest.eu/">Aquaforest</a></h1>
               <div class="timestamp">Generated: ${message.timestamp.toLocaleString()}</div>
             </div>
            <div class="content">${htmlContent}</div>
          </body>
        </html>
      `;

      printWindow.document.write(fullHtmlContent);
      printWindow.document.close();
      
      // Wait a bit for content to load, then print
      setTimeout(() => {
        printWindow.print();
        printWindow.close();
      }, 250);
    } catch (err) {
      console.error('Failed to generate PDF: ', err);
    }
  };

  return (
    <div className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} mb-4 sm:mb-6`}>
      <div className={`flex items-start ${message.type === 'user' ? 'space-x-3 sm:space-x-4 flex-row-reverse space-x-reverse' : 'space-x-2 sm:space-x-4'} max-w-[90%] sm:max-w-3xl`}>
        {/* Avatar - ukryty na mobile */}
        <div className="hidden sm:flex w-10 h-10 rounded-2xl bg-gradient-to-br from-brand-600 via-brand-700 to-brand-800 items-center justify-center flex-shrink-0 shadow-brand">
          {message.type === 'user' ? (
            <User className="w-5 h-5 text-white" />
          ) : (
            <div className="circle">
              <div className="wave"></div>
            </div>
          )}
        </div>
        
        <div className="flex flex-col space-y-2 min-w-0 flex-1">
          <div className={`rounded-2xl sm:rounded-3xl px-4 sm:px-6 py-3 sm:py-4 shadow-sm backdrop-blur-md border break-words transition-all duration-300 hover:shadow-lg ${
            message.type === 'user'
              ? 'bg-gradient-to-r from-brand-600 to-brand-700 text-white border-brand-500/20 hover:shadow-brand'
              : 'bg-white/95 text-gray-800 border-brand-200/40 hover:border-brand-300/60'
          }`}>
            {/* 🆕 Wyświetlanie pliku jeśli jest dostępny */}
            {message.imageUrl && (
              <MessageFileDisplay 
                imageUrl={message.imageUrl}
                fileName={message.fileName}
                fileType={message.fileType}
                fileSize={message.fileSize}
              />
            )}
            
            {message.type === 'assistant' ? (
              <TruncatedMessageContent 
                content={message.content} 
                isUser={false} 
              />
            ) : (
              <MessageContent 
                content={message.content} 
                isUser={true} 
              />
            )}
          </div>
          
          <div className={`flex items-center ${
            message.type === 'user' ? 'justify-end' : 'justify-between'
          } px-2`}>
            <p className={`text-xs transition-colors duration-300 ${
              message.type === 'user' ? 'text-brand-300' : 'text-gray-500'
            }`}>
              {message.timestamp.toLocaleTimeString('en-US', { 
                hour: '2-digit', 
                minute: '2-digit' 
              })}
            </p>
            
            {/* Action buttons for AI messages only */}
            {message.type === 'assistant' && (
              <div className="flex items-center space-x-2">
                <button
                  onClick={handleCopy}
                  className="p-1.5 text-gray-400 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-all duration-300 transform hover:scale-110 active:scale-95 hover:shadow-brand"
                  title="Copy response"
                >
                  <Copy className="w-4 h-4" />
                </button>
                <button
                  onClick={handleDownloadPDF}
                  className="p-1.5 text-gray-400 hover:text-brand-600 hover:bg-brand-50 rounded-lg transition-all duration-300 transform hover:scale-110 active:scale-95 hover:shadow-brand"
                  title="Download as PDF"
                >
                  <Download className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Message 