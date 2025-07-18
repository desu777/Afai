import React from 'react';
import { Copy, ArrowRight } from 'lucide-react';

interface ExamplesPanelProps {
  onExampleSelect: (example: string) => void;
}

const ExamplesPanel: React.FC<ExamplesPanelProps> = ({ onExampleSelect }) => {
  const examples = [
    {
      category: "New Tank Setup",
      questions: [
        "I want to build a new tank, how should I use Pro Bio S in the early stages?",
        "What products do I need for cycling a new reef tank?",
        "How to set up the Balling Method for a new SPS tank?",
        "What's the best salt for a new mixed reef aquarium?"
      ]
    },
    {
      category: "Nutrient Control",
      questions: [
        "What is the best product to lower nitrate levels?",
        "How to reduce phosphate levels without harming corals?",
        "My tank has high NO3 and PO4, should I use AF NitraPhos Minus or Pro Bio S?",
        "How to balance N:P ratio in ULNS system?"
      ]
    },
    {
      category: "Water Chemistry",
      questions: [
        "How to raise calcium levels in my reef tank?",
        "My KH is dropping daily, what should I do?",
        "What's the difference between Component 1+2+3+ and Components Pro?",
        "How to stabilize pH in my reef tank?"
      ]
    },
    {
      category: "Coral Care",
      questions: [
        "My SPS corals are pale, which supplements should I use?",
        "How to enhance coral coloration naturally?",
        "What's the best feeding schedule for LPS corals?",
        "How to recover corals after a parameter swing?"
      ]
    },
    {
      category: "Troubleshooting",
      questions: [
        "I'm using Pro Bio S and -NP Pro for a month, but I got green-brown stuff on rocks. Should I reduce dosage or stop completely?",
        "My corals are browning after starting probiotic method, what's wrong?",
        "Algae outbreak after adding new fish, how to fix it?",
        "Why are my test results inconsistent with ICP analysis?"
      ]
    },
    {
      category: "Product Selection",
      questions: [
        "What's better for iron supplementation: Iron or Ferrum Lab?",
        "Should I use Reef Salt or Reef Salt Plus for my setup?",
        "Difference between AF Build and calcium supplements?",
        "Which trace element supplements are essential for SPS?"
      ]
    },
    {
      category: "Advanced Questions",
      questions: [
        "Analyze my ICP results: [upload your ICP PDF file]",
        "How to dose Components Strong with Balling Method?",
        "What's the optimal dosing schedule for AF Energy and Vitality?",
        "How to transition from two-part to Balling Method?"
      ]
    }
  ];

  const handleCopyExample = (example: string) => {
    navigator.clipboard.writeText(example);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Scrollable Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto p-6">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-4">
              AF AI Examples
            </h1>
            <p className="text-gray-600 text-lg">
              Get inspired by these example questions to make the most of your reef aquarium consultation.
              Click on any question to use it directly or copy it to modify.
            </p>
          </div>
          
          <div className="grid gap-8">
            {examples.map((category, categoryIndex) => (
              <div key={categoryIndex} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                  <div className="w-2 h-2 bg-purple-500 rounded-full mr-3"></div>
                  {category.category}
                </h2>
                
                <div className="space-y-3">
                  {category.questions.map((question, questionIndex) => (
                    <div 
                      key={questionIndex}
                      className="group flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-brand-50 transition-all duration-300 cursor-pointer transform hover:scale-[1.02] hover:shadow-brand"
                      onClick={() => onExampleSelect(question)}
                    >
                      <div className="flex-1 mr-4">
                        <p className="text-gray-700 group-hover:text-brand-700 transition-colors duration-300">
                          {question}
                        </p>
                      </div>
                      
                      <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleCopyExample(question);
                          }}
                          className="p-2 text-gray-400 hover:text-brand-600 transition-all duration-300 transform hover:scale-110 active:scale-95 rounded-lg hover:bg-brand-100"
                          title="Copy question"
                        >
                          <Copy className="w-4 h-4" />
                        </button>
                        
                        <ArrowRight className="w-4 h-4 text-brand-500" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
          
          {/* Tips Section */}
          <div className="mt-12 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-8">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Tips for Better Results
            </h3>
            <ul className="space-y-3 text-gray-700">
              <li className="flex items-start">
                <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <span>Be specific about your tank size, type (SPS/LPS/mixed), and current parameters</span>
              </li>
              <li className="flex items-start">
                <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <span>Include your current dosing schedule and products you're already using</span>
              </li>
              <li className="flex items-start">
                <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <span>Mention any recent changes or problems you've noticed</span>
              </li>
              <li className="flex items-start">
                <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 mr-3 flex-shrink-0"></div>
                <span>For ICP analysis, upload your PDF file with complete results</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExamplesPanel; 