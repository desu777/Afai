import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { ExternalLink } from 'lucide-react'

interface MessageContentProps {
  content: string
  isUser: boolean
}

const MessageContent: React.FC<MessageContentProps> = ({ content, isUser }) => {
  if (isUser) {
    // User messages - plain text, no markdown, white text for purple background
    return (
      <p className="text-sm leading-relaxed font-medium whitespace-pre-wrap text-white">
        {content}
      </p>
    )
  }

  // AI messages - render markdown
  return (
    <div className="text-sm leading-relaxed font-medium">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Headings
          h1: ({ children }) => (
            <h1 className="text-lg font-bold text-gray-900 mt-4 mb-2 first:mt-0">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-base font-bold text-gray-900 mt-4 mb-2 first:mt-0">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-sm font-bold text-purple-700 mt-3 mb-2 first:mt-0">
              {children}
            </h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-sm font-semibold text-gray-800 mt-3 mb-1 first:mt-0">
              {children}
            </h4>
          ),
          
          // Paragraphs
          p: ({ children }) => (
            <p className="mb-3 last:mb-0">
              {children}
            </p>
          ),
          
          // Links with external icon
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-purple-600 hover:text-purple-800 font-medium underline decoration-purple-300 hover:decoration-purple-500 transition-colors duration-200"
            >
              {children}
              <ExternalLink className="w-3 h-3 flex-shrink-0" />
            </a>
          ),
          
          // Lists
          ul: ({ children }) => (
            <ul className="list-disc list-inside mb-3 space-y-1 ml-2">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-inside mb-3 space-y-1 ml-2">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="text-gray-700">
              {children}
            </li>
          ),
          
          // Bold text
          strong: ({ children }) => (
            <strong className="font-bold text-gray-900">
              {children}
            </strong>
          ),
          
          // Italic text
          em: ({ children }) => (
            <em className="italic text-gray-700">
              {children}
            </em>
          ),
          
          // Code
          code: ({ children }) => (
            <code className="bg-purple-50 text-purple-700 px-2 py-1 rounded text-xs font-mono">
              {children}
            </code>
          ),
          
          // Code blocks
          pre: ({ children }) => (
            <pre className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-3 overflow-x-auto">
              {children}
            </pre>
          ),
          
          // Horizontal rule
          hr: () => (
            <hr className="border-purple-200 my-4" />
          ),
          
          // Blockquotes
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-purple-300 pl-4 mb-3 italic text-gray-600">
              {children}
            </blockquote>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

export default MessageContent 