import React, { useState, useMemo } from 'react'
import { ChevronDown, ChevronUp } from 'lucide-react'
import MessageContent from './MessageContent'

interface TruncatedMessageContentProps {
  content: string
  isUser: boolean
}

interface ContentSection {
  type: 'regular' | 'collapsible'
  content: string
  id: string
}

const TruncatedMessageContent: React.FC<TruncatedMessageContentProps> = ({ 
  content, 
  isUser
}) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set())

  const contentSections = useMemo(() => {
    // Jeśli to user message, nie przycinamy
    if (isUser) {
      return [{
        type: 'regular' as const,
        content: content,
        id: 'user-content'
      }]
    }

    // Znajdź wszystkie sekcje [SHOW_MORE_START]...[SHOW_MORE_END]
    const showMoreRegex = /\[SHOW_MORE_START\](.*?)\[SHOW_MORE_END\]/gs
    const sections: ContentSection[] = []
    let lastIndex = 0
    let match
    let sectionIndex = 0

    while ((match = showMoreRegex.exec(content)) !== null) {
      // Dodaj treść przed sekcją collapsible
      if (match.index > lastIndex) {
        const regularContent = content.slice(lastIndex, match.index).trim()
        if (regularContent) {
          sections.push({
            type: 'regular',
            content: regularContent,
            id: `regular-${sectionIndex}`
          })
        }
      }

      // Dodaj sekcję collapsible
      sections.push({
        type: 'collapsible',
        content: match[1].trim(),
        id: `collapsible-${sectionIndex}`
      })

      lastIndex = match.index + match[0].length
      sectionIndex++
    }

    // Dodaj pozostałą treść po ostatniej sekcji collapsible
    if (lastIndex < content.length) {
      const remainingContent = content.slice(lastIndex).trim()
      if (remainingContent) {
        sections.push({
          type: 'regular',
          content: remainingContent,
          id: `regular-${sectionIndex}`
        })
      }
    }

    // Jeśli nie znaleziono żadnych sekcji collapsible, zwróć całą treść jako regular
    if (sections.length === 0) {
      return [{
        type: 'regular' as const,
        content: content,
        id: 'regular-only'
      }]
    }

    return sections
  }, [content, isUser])

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev)
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId)
      } else {
        newSet.add(sectionId)
      }
      return newSet
    })
  }

  return (
    <div className="space-y-3">
      {contentSections.map((section) => (
        <div key={section.id}>
          {section.type === 'regular' ? (
            <MessageContent content={section.content} isUser={isUser} />
          ) : (
            <div className="space-y-2">
              <button
                onClick={() => toggleSection(section.id)}
                className="flex items-center gap-2 text-xs font-medium text-purple-600 hover:text-purple-800 transition-colors duration-200 bg-purple-50 hover:bg-purple-100 px-3 py-2 rounded-lg border border-purple-200/40 hover:border-purple-300/60"
              >
                <span>{expandedSections.has(section.id) ? 'Show less' : 'Show more'}</span>
                {expandedSections.has(section.id) ? (
                  <ChevronUp className="w-3 h-3" />
                ) : (
                  <ChevronDown className="w-3 h-3" />
                )}
              </button>
              
              {expandedSections.has(section.id) && (
                <div className="pl-4 border-l-2 border-purple-200">
                  <MessageContent content={section.content} isUser={false} />
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  )
}

export default TruncatedMessageContent