import React, { useState, useMemo } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import MessageContent from './MessageContent'

interface TruncatedMessageContentProps {
  content: string
  isUser: boolean
  maxCharsAfterFirstLink?: number
}

const TruncatedMessageContent: React.FC<TruncatedMessageContentProps> = ({ 
  content, 
  isUser, 
  maxCharsAfterFirstLink = 50 
}) => {
  const [isExpanded, setIsExpanded] = useState(false)

  const { shouldTruncate, truncatedContent, fullContent } = useMemo(() => {
    // Jeśli to user message, nie przycinamy
    if (isUser) {
      return {
        shouldTruncate: false,
        truncatedContent: content,
        fullContent: content
      }
    }

    // Szukamy pierwszego markdown linka: [text](url)
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/
    const linkMatch = content.match(linkRegex)
    
    if (!linkMatch) {
      // Brak linków - nie przycinamy
      return {
        shouldTruncate: false,
        truncatedContent: content,
        fullContent: content
      }
    }

    const linkEndIndex = linkMatch.index! + linkMatch[0].length
    const remainingContent = content.slice(linkEndIndex)
    
    // Sprawdzamy czy pozostała treść po linku jest dłuższa niż maxCharsAfterFirstLink
    if (remainingContent.length <= maxCharsAfterFirstLink) {
      return {
        shouldTruncate: false,
        truncatedContent: content,
        fullContent: content
      }
    }

    // Tworzymy skróconą wersję
    const beforeAndLink = content.slice(0, linkEndIndex)
    const truncatedRemainder = remainingContent.slice(0, maxCharsAfterFirstLink)
    const truncated = beforeAndLink + truncatedRemainder + '...'

    return {
      shouldTruncate: true,
      truncatedContent: truncated,
      fullContent: content
    }
  }, [content, isUser, maxCharsAfterFirstLink])

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded)
  }

  return (
    <div className="space-y-3">
      <MessageContent 
        content={isExpanded ? fullContent : truncatedContent} 
        isUser={isUser} 
      />
      
      {shouldTruncate && (
        <button
          onClick={toggleExpanded}
          className="flex items-center gap-2 text-xs font-medium text-purple-600 hover:text-purple-800 transition-colors duration-200 bg-purple-50 hover:bg-purple-100 px-3 py-2 rounded-lg border border-purple-200/40 hover:border-purple-300/60"
        >
          <span>{isExpanded ? 'Show less' : 'Show more'}</span>
          {isExpanded ? (
            <ChevronUp className="w-3 h-3" />
          ) : (
            <ChevronDown className="w-3 h-3" />
          )}
        </button>
      )}
    </div>
  )
}

export default TruncatedMessageContent