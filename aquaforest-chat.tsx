import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Fish, Settings, MoreVertical, User, Bot, Loader2 } from 'lucide-react';

const AquaforestChat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: '🐠 Welcome! I\'m AF AI, your Aquaforest assistant. I can help you with aquarium products, dosing calculations, and problem solving in any language. How can I help you today?',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Symulacja odpowiedzi od AI
    setTimeout(() => {
      const aiResponse = {
        id: messages.length + 2,
        type: 'assistant',
        content: getSimulatedResponse(inputValue),
        timestamp: new Date()
      };
      setMessages(prev => [...prev, aiResponse]);
      setIsLoading(false);
    }, 1000 + Math.random() * 2000);
  };

  const getSimulatedResponse = (query) => {
    const responses = [
      "Based on your query, I recommend checking AF Ca Plus products for calcium level correction. Dosage: 10ml per 100L aquarium. Would you like to know more details?",
      "I see you have algae problems. I recommend AF NitraPhos Minus and Pro Bio S. These products effectively combat excess nutrients. Do you need help with dosing?",
      "For marine aquariums, I recommend the Component 1+2+3+ system which ensures stable Ca, Mg, and KH parameters. It's the Balling method for advanced aquarists.",
      "For beginners, I recommend AF Perfect Water and Bio S for filter colonization. How big is your aquarium?",
      "AF Amino Mix is an excellent choice for coral coloration. Dosage: 1 drop per 100L daily. Monitor coral response carefully."
    ];
    return responses[Math.floor(Math.random() * responses.length)];
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const suggestedQueries = [
    "How to raise calcium levels?",
    "Algae problems solutions",
    "AF Build dosing guide",
    "Products for beginners"
  ];

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-slate-50 via-purple-50 to-violet-100">
      {/* Header */}
      <div className="bg-white/95 backdrop-blur-md border-b border-purple-200/50 px-4 sm:px-6 py-5 shadow-sm">
        <div className="flex items-center justify-between max-w-5xl mx-auto">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 rounded-2xl flex items-center justify-center shadow-lg">
              <Fish className="w-7 h-7 text-white" />
            </div>
            <div className="flex flex-col">
              <h1 className="text-xl font-bold text-gray-900 tracking-tight">AF AI Assistant</h1>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <p className="text-sm text-purple-700 font-medium">Aquaforest • Multi-language support</p>
              </div>
            </div>
          </div>
          <div className="flex items-center space-x-1">
            <button className="p-2.5 hover:bg-purple-100 rounded-xl transition-all duration-200 hover:scale-105">
              <Settings className="w-5 h-5 text-gray-600" />
            </button>
            <button className="p-2.5 hover:bg-purple-100 rounded-xl transition-all duration-200 hover:scale-105">
              <MoreVertical className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {messages.length === 1 && (
            <div className="text-center mb-12">
              <div className="inline-flex items-center space-x-3 bg-white/80 backdrop-blur-md rounded-2xl px-8 py-4 shadow-lg border border-purple-200/50 mb-8">
                <Sparkles className="w-6 h-6 text-purple-600" />
                <span className="text-gray-800 font-semibold text-lg">Start conversation with AF AI</span>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mx-auto">
                {suggestedQueries.map((query, index) => (
                  <button
                    key={index}
                    onClick={() => setInputValue(query)}
                    className="group bg-white/90 hover:bg-white backdrop-blur-md border border-purple-200/60 hover:border-purple-400 rounded-2xl px-6 py-4 text-sm text-gray-700 hover:text-gray-900 transition-all duration-300 hover:shadow-lg hover:scale-[1.02] text-left"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{query}</span>
                      <Send className="w-4 h-4 text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                    </div>
                  </button>
                ))}
              </div>
              <div className="mt-6 text-center">
                <p className="text-sm text-purple-600 font-medium bg-purple-50/80 rounded-2xl px-6 py-3 inline-block backdrop-blur-md border border-purple-200/40">
                  🌍 I speak all languages! Ask me in English, Polish, German, French, Spanish, and more
                </p>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
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
                    <p className="text-sm leading-relaxed font-medium">{message.content}</p>
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
          ))}

          {isLoading && (
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
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="bg-white/95 backdrop-blur-md border-t border-purple-200/50 px-4 sm:px-6 py-6 shadow-lg">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end space-x-4">
            <div className="flex-1 relative">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your message to AF AI in any language..."
                className="w-full resize-none rounded-3xl bg-white/95 backdrop-blur-md border border-purple-200/60 focus:border-purple-500 focus:ring-4 focus:ring-purple-100/50 outline-none px-6 py-4 pr-16 text-gray-800 placeholder-gray-500 shadow-md transition-all duration-200 font-medium"
                rows="1"
                style={{ 
                  minHeight: '56px', 
                  maxHeight: '140px',
                  lineHeight: '1.5'
                }}
                disabled={isLoading}
              />
              <div className="absolute right-3 bottom-3 flex items-center space-x-2">
                <div className="text-xs text-gray-400 bg-gray-100/80 px-2 py-1 rounded-lg">
                  Enter
                </div>
              </div>
            </div>
            <button
              onClick={handleSend}
              disabled={!inputValue.trim() || isLoading}
              className="w-14 h-14 bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 hover:from-purple-700 hover:via-purple-800 hover:to-violet-900 disabled:from-gray-400 disabled:via-gray-500 disabled:to-gray-600 disabled:cursor-not-allowed rounded-2xl flex items-center justify-center shadow-lg transition-all duration-200 hover:shadow-xl hover:scale-105 active:scale-95"
            >
              <Send className="w-6 h-6 text-white" />
            </button>
          </div>
          <div className="flex items-center justify-center mt-4 space-x-3">
            <div className="w-2 h-2 bg-purple-300 rounded-full"></div>
            <p className="text-xs text-gray-500 text-center font-medium">
              AF AI can make mistakes. Verify important information in product documentation.
            </p>
            <div className="w-2 h-2 bg-purple-300 rounded-full"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AquaforestChat;