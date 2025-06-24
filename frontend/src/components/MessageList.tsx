import React from 'react'
import { Message as MessageType, WorkflowUpdate } from '../types'
import Message from './Message'
import LoadingMessage from './LoadingMessage'
import StreamingLoadingMessage from './StreamingLoadingMessage'
import SuggestedQueries from './SuggestedQueries'

interface MessageListProps {
  messages: MessageType[];
  isLoading: boolean;
  onQuerySelect: (query: string) => void;
  currentWorkflowUpdate?: WorkflowUpdate;
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading, onQuerySelect, currentWorkflowUpdate }) => {

  return (
    <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-8">
      <div className="max-w-4xl mx-auto space-y-8">
        {messages.length === 0 && (
          <SuggestedQueries onQuerySelect={onQuerySelect} />
        )}

        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}

        {isLoading && (
          currentWorkflowUpdate 
            ? <StreamingLoadingMessage currentUpdate={currentWorkflowUpdate} />
            : <LoadingMessage />
        )}
      </div>
    </div>
  );
};

export default MessageList 