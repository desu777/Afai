import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MessageContentProps {
  content: string;
  isUser: boolean;
}

export const MessageContent: React.FC<MessageContentProps> = ({ content, isUser }) => {
  if (isUser) {
    // User messages - plain text, no markdown
    return (
      <p className="text-sm leading-relaxed font-medium whitespace-pre-wrap break-words">
        {content}
      </p>
    );
  }

  // AI messages - render markdown
  return (
    <div className="text-sm leading-relaxed font-medium break-words overflow-hidden">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Headings
          h1: ({ children }) => (
            <h1 className="text-lg font-bold text-gray-900 mt-4 mb-2 first:mt-0 break-words">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-base font-bold text-gray-900 mt-4 mb-2 first:mt-0 break-words">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-sm font-bold text-gray-900 mt-3 mb-2 first:mt-0 break-words" style={{ color: 'var(--af-primary)' }}>
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-sm font-semibold text-gray-800 mt-3 mb-1 first:mt-0 break-words">
              {children}
            </h4>
          ),
          
          // Paragraphs
          p: ({ children }) => (
            <p className="mb-3 last:mb-0 break-words">
              {children}
            </p>
          ),
          
          // Links - clean URL text only, no icons
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium underline transition-colors duration-200 break-all"
              style={{ 
                color: 'var(--af-primary)', 
                textDecorationColor: 'var(--af-primary)',
                opacity: 0.9
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.opacity = '1';
                e.currentTarget.style.color = 'var(--af-primary-hover)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.opacity = '0.9';
                e.currentTarget.style.color = 'var(--af-primary)';
              }}
            >
              <span className="break-words">{children}</span>
            </a>
          ),
          
          // Lists
          ul: ({ children }) => (
            <ul className="list-disc list-inside mb-3 space-y-1 ml-2 break-words">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-inside mb-3 space-y-1 ml-2 break-words">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="text-gray-700 break-words mb-1">
              {children}
            </li>
          ),
          
          // Bold text
          strong: ({ children }) => (
            <strong className="font-bold text-gray-900 break-words">
              {children}
            </strong>
          ),
          
          // Italic text
          em: ({ children }) => (
            <em className="italic text-gray-700 break-words">
              {children}
            </em>
          ),
          
          // Code
          code: ({ children }) => (
            <code className="px-1.5 py-0.5 rounded text-xs font-mono break-all" style={{ backgroundColor: 'rgba(71, 21, 76, 0.1)', color: 'var(--af-primary)' }}>
              {children}
            </code>
          ),
          
          // Code blocks
          pre: ({ children }) => (
            <pre className="bg-gray-50 border border-gray-200 rounded-lg p-3 mb-3 overflow-x-auto max-w-full">
              {children}
            </pre>
          ),
          
          // Horizontal rule
          hr: () => (
            <hr className="my-4" style={{ borderColor: 'var(--af-primary)', opacity: 0.3 }} />
          ),
          
          // Blockquotes
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 pl-4 mb-3 italic text-gray-600 break-words" style={{ borderColor: 'var(--af-primary)', opacity: 0.8 }}>
              {children}
            </blockquote>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};