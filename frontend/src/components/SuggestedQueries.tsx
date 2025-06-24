import React, { useState } from 'react'
import { Info, X } from 'lucide-react'

interface SuggestedQueriesProps {
  onQuerySelect: (query: string) => void;
}

const SuggestedQueries: React.FC<SuggestedQueriesProps> = ({ onQuerySelect }) => {
  const [showVersionModal, setShowVersionModal] = useState(false);

  const bubbleQueries = [
    {
      id: 1,
      title: "Water Parameters",
      question: "How to raise calcium levels in my reef tank?",
      color: "#9333ea" // purple-600
    },
    {
      id: 2, 
      title: "Algae Control",
      question: "Best solutions for green algae problems?",
      color: "#7c3aed" // purple-700
    },
    {
      id: 3,
      title: "Product Dosing", 
      question: "AF Build dosing guide for beginners?",
      color: "#5b21b6" // violet-800
    }
  ];

  return (
    <div className="text-center mb-12">
      <div className="inline-flex items-center space-x-3 bg-white/80 backdrop-blur-md rounded-2xl px-8 py-4 shadow-lg border border-purple-200/50 mb-8">
        <div className="w-6 h-6 rounded-full bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 flex items-center justify-center shadow-sm">
          <div className="circle">
            <div className="wave"></div>
          </div>
        </div>
        <span className="text-gray-800 font-semibold text-lg">Start conversation with AF AI</span>
        
        {/* Version Badge and Info Button */}
        <div className="flex items-center space-x-2 ml-4">
          <div className="bg-gradient-to-r from-purple-600 to-violet-700 text-white text-xs font-bold px-3 py-1 rounded-full shadow-sm">
            v1.2
          </div>
          <button
            onClick={() => setShowVersionModal(true)}
            className="p-1.5 hover:bg-purple-100 rounded-full transition-colors duration-200 text-purple-600 hover:text-purple-700"
            title="What's new in v1.2?"
          >
            <Info className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      <div className="bubble-container">
        {bubbleQueries.map((bubble) => (
          <div 
            key={bubble.id}
            className="bubble-card"
            style={{"--clr": bubble.color} as React.CSSProperties}
            onClick={() => onQuerySelect(bubble.question)}
          >
            <div className="bubble-number">
              {String(bubble.id).padStart(2, '0')}
            </div>
            <p className="bubble-text">
              {bubble.question}
            </p>
            <button className="bubble-button">
              Ask AI
          </button>
          </div>
        ))}
      </div>
      
      <div className="mt-8 text-center">
        <p className="text-sm text-purple-600 font-medium bg-purple-50/80 rounded-2xl px-6 py-3 inline-block backdrop-blur-md border border-purple-200/40">
          I speak all languages! Ask me in English, Polish, German, French, Spanish, and more
        </p>
      </div>

      {/* Version Modal */}
      {showVersionModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl shadow-2xl border border-purple-200/50 max-w-lg w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 flex items-center justify-center shadow-lg">
                    <div className="circle">
                      <div className="wave"></div>
                    </div>
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-900">AF AI v1.2</h2>
                    <p className="text-sm text-purple-600">What's new in this version?</p>
                  </div>
                </div>
                <button
                  onClick={() => setShowVersionModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-xl transition-colors"
                >
                  <X className="w-5 h-5 text-gray-500" />
                </button>
              </div>

              {/* Features List */}
              <div className="space-y-4">
                <div className="flex items-start space-x-3 p-4 bg-purple-50/50 rounded-2xl border border-purple-200/30">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                    1
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">🎭 Passionate Aquaforest Expert</h3>
                    <p className="text-sm text-gray-600">Neutral personality changed to an enthusiastic Aquaforest expert who is passionate about aquaristics and eager to share knowledge.</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 p-4 bg-purple-50/50 rounded-2xl border border-purple-200/30">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                    2
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">🧠 Intelligent Business Reasoner</h3>
                    <p className="text-sm text-gray-600">Advanced system for selecting Aquaforest products based on your problem, aquarium type, and needs.</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 p-4 bg-purple-50/50 rounded-2xl border border-purple-200/30">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                    3
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">💬 Natural Conversation Flow</h3>
                    <p className="text-sm text-gray-600">Smooth conversation continuations with intelligent follow-up system that remembers context and answers additional questions.</p>
                  </div>
                </div>

                <div className="flex items-start space-x-3 p-4 bg-purple-50/50 rounded-2xl border border-purple-200/30">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-violet-600 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                    4
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">🔬 ICP Analysis Results</h3>
                    <p className="text-sm text-gray-600 mb-2">Paste a link to your water analysis results and get personalized product recommendations!</p>
                    <div className="bg-white/80 rounded-xl p-3 border border-purple-200/40">
                      <p className="text-xs text-purple-700 font-mono">
                        "Analyze my results: <br/>
                        https://aquaforestlab.com/pl/results/v6GMFwU876171"
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="mt-6 pt-4 border-t border-purple-200/30">
                <p className="text-xs text-gray-500 text-center">
                  Aquaforest AI Assistant • Continuously improving our assistant
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SuggestedQueries 