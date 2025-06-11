import React from 'react'

interface SuggestedQueriesProps {
  onQuerySelect: (query: string) => void;
}

const SuggestedQueries: React.FC<SuggestedQueriesProps> = ({ onQuerySelect }) => {
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
    </div>
  );
};

export default SuggestedQueries 