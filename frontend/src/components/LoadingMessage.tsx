import { Bot, Loader2 } from 'lucide-react'

const LoadingMessage: React.FC = () => {
  return (
    <div className="flex justify-start mb-6">
      <div className="flex items-start space-x-4 max-w-3xl">
        <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 flex items-center justify-center shadow-md">
          <Bot className="w-5 h-5 text-white" />
        </div>
        <div className="rounded-3xl px-6 py-4 bg-white/95 backdrop-blur-md border border-purple-200/40 shadow-sm">
          <div className="flex items-center space-x-3">
            <Loader2 className="w-5 h-5 text-purple-600 animate-spin" />
            <span className="text-gray-700 text-sm font-medium">AF AI is thinking...</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingMessage 