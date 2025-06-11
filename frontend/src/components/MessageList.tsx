import { useRef, useEffect } from 'react'
import { Message as MessageType } from '../types'
import Message from './Message'
import LoadingMessage from './LoadingMessage'
import SuggestedQueries from './SuggestedQueries'

interface MessageListProps {
  messages: MessageType[];
  isLoading: boolean;
  onQuerySelect: (query: string) => void;
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading, onQuerySelect }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {messages.length === 1 && (
          <SuggestedQueries onQuerySelect={onQuerySelect} />
        )}

        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}

        {isLoading && <LoadingMessage />}
        
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
};

export default MessageList 