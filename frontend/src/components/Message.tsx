import { User, Bot } from 'lucide-react'
import { Message as MessageType } from '../types'
import MessageContent from './MessageContent'

interface MessageProps {
  message: MessageType;
}

const Message: React.FC<MessageProps> = ({ message }) => {
  return (
    <div
      className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'} mb-6`}
    >
      <div className={`flex items-start space-x-4 max-w-3xl ${message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
        <div className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md ${
          message.type === 'user' 
            ? 'bg-gradient-to-br from-gray-600 via-gray-700 to-gray-800' 
            : 'bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800'
        }`}>
          {message.type === 'user' ? (
            <User className="w-5 h-5 text-white" />
          ) : (
            <Bot className="w-5 h-5 text-white" />
          )}
        </div>
        <div className="flex flex-col space-y-2">
          <div className={`rounded-3xl px-6 py-4 shadow-sm backdrop-blur-md border ${
            message.type === 'user'
              ? 'bg-gradient-to-r from-purple-600 to-violet-700 text-white border-purple-500/20'
              : 'bg-white/95 text-gray-800 border-purple-200/40'
          }`}>
            <MessageContent 
              content={message.content} 
              isUser={message.type === 'user'} 
            />
          </div>
          <p className={`text-xs px-2 ${
            message.type === 'user' ? 'text-right text-purple-300' : 'text-left text-gray-500'
          }`}>
            {message.timestamp.toLocaleTimeString('en-US', { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </p>
        </div>
      </div>
    </div>
  );
};

export default Message 