import React, { useState, useMemo } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { MessageContent } from './MessageContent';

interface TruncatedMessageContentProps {
  content: string;
  isUser: boolean;
}

interface ContentSection {
  type: 'regular' | 'collapsible';
  content: string;
  id: string;
}

export const TruncatedMessageContent: React.FC<TruncatedMessageContentProps> = ({ 
  content, 
  isUser
}) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  const contentSections = useMemo(() => {
    // Jeśli to user message, nie przycinamy
    if (isUser) {
      return [{
        type: 'regular' as const,
        content: content,
        id: 'user-content'
      }];
    }

    // Znajdź wszystkie sekcje [SHOW_MORE_START]...[SHOW_MORE_END]
    const showMoreRegex = /\[SHOW_MORE_START\](.*?)\[SHOW_MORE_END\]/gs;
    const sections: ContentSection[] = [];
    let lastIndex = 0;
    let match;
    let sectionIndex = 0;

    while ((match = showMoreRegex.exec(content)) !== null) {
      // Dodaj treść przed sekcją collapsible
      if (match.index > lastIndex) {
        const regularContent = content.slice(lastIndex, match.index).trim();
        if (regularContent) {
          sections.push({
            type: 'regular',
            content: regularContent,
            id: `regular-${sectionIndex}`
          });
        }
      }

      // Dodaj sekcję collapsible
      sections.push({
        type: 'collapsible',
        content: match[1].trim(),
        id: `collapsible-${sectionIndex}`
      });

      lastIndex = match.index + match[0].length;
      sectionIndex++;
    }

    // Dodaj pozostałą treść po ostatniej sekcji collapsible
    if (lastIndex < content.length) {
      const remainingContent = content.slice(lastIndex).trim();
      if (remainingContent) {
        sections.push({
          type: 'regular',
          content: remainingContent,
          id: `regular-${sectionIndex}`
        });
      }
    }

    // Jeśli nie znaleziono żadnych sekcji collapsible, zwróć całą treść jako regular
    if (sections.length === 0) {
      return [{
        type: 'regular' as const,
        content: content,
        id: 'regular-only'
      }];
    }

    return sections;
  }, [content, isUser]);

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  };

  return (
    <div className="af-truncated-content">
      {contentSections.map((section) => (
        <div key={section.id}>
          {section.type === 'regular' ? (
            <MessageContent content={section.content} isUser={isUser} />
          ) : (
            <div className="af-collapsible-section">
              <button
                onClick={() => toggleSection(section.id)}
                className="af-show-more-button"
              >
                <span>{expandedSections.has(section.id) ? 'Show Less' : 'Read More'}</span>
                {expandedSections.has(section.id) ? (
                  <ChevronUp className="af-show-more-icon" />
                ) : (
                  <ChevronDown className="af-show-more-icon" />
                )}
              </button>
              
              {expandedSections.has(section.id) && (
                <div className="af-expanded-content">
                  <MessageContent content={section.content} isUser={false} />
                </div>
              )}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};