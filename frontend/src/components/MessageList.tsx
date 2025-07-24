import React from 'react'
import { Message as MessageType, WorkflowUpdate } from '../types'
import Message from './Message'
import StreamingLoadingMessage from './StreamingLoadingMessage'
import SkeletonLoadingMessage from './SkeletonLoadingMessage'
import WelcomeScreen from './WelcomeScreen'

interface MessageListProps {
  messages: MessageType[];
  isLoading: boolean;
  currentWorkflowUpdate?: WorkflowUpdate;
  inputValue: string;
  onInputChange: (value: string) => void;
  onSend: () => void;
  selectedImage?: File | null;
  onImageSelect?: (image: File | null) => void;
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading, currentWorkflowUpdate, inputValue, onInputChange, onSend, selectedImage, onImageSelect }) => {

  // 🔍 DEBUG: Log currentWorkflowUpdate
  if (import.meta.env.VITE_TEST_ENV === 'true' && currentWorkflowUpdate) {
    console.log('📋 [MessageList] currentWorkflowUpdate received:', currentWorkflowUpdate);
  }

  const hasMessages = messages.length > 0 || isLoading;

  return (
    <div 
      data-messages-list
      className={`h-full overflow-y-auto px-2 sm:px-4 md:px-6 pt-20 ${hasMessages ? 'pb-64' : 'pb-4'}`}
    >
      <div className="max-w-4xl mx-auto space-y-4 sm:space-y-6 md:space-y-8">
        {/* Welcome Screen - only show when no messages */}
        {messages.length === 0 && !isLoading && (
          <WelcomeScreen 
            inputValue={inputValue}
            isLoading={isLoading}
            onInputChange={onInputChange}
            onSend={onSend}
            selectedImage={selectedImage}
            onImageSelect={onImageSelect}
          />
        )}

        {messages.map((message) => (
          <Message key={message.id} message={message} />
        ))}

        {isLoading && (
          <>
            {import.meta.env.VITE_TEST_ENV === 'true' && (
              console.log('🔄 [MessageList] isLoading=true, currentWorkflowUpdate=', currentWorkflowUpdate)
            )}
            {currentWorkflowUpdate 
              ? <StreamingLoadingMessage currentUpdate={currentWorkflowUpdate} />
              : <SkeletonLoadingMessage />}
          </>
        )}
      </div>
    </div>
  );
};

export default MessageList 