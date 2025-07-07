import React from 'react'
import { Calendar, Star, Zap, Bug, Shield, Smartphone } from 'lucide-react'

interface Update {
  version: string;
  date: string;
  type: 'major' | 'minor' | 'patch';
  title: string;
  description: string;
  changes: {
    category: 'new' | 'improved' | 'fixed' | 'security';
    items: string[];
  }[];
}

const updates: Update[] = [
  {
    version: "1.4V",
    date: "2025-07-07",
    type: "minor",
    title: "🚀 Professional AI Model Upgrade & Visual Diagnostics",
    description: "Revolutionary upgrade to professional Gemini-2.5-Flash model with dramatic performance improvements and new visual diagnostic capabilities for comprehensive aquarium problem analysis.",
    changes: [
      {
        category: "new",
        items: [
          "📸 Visual Diagnostics - Upload photos of your aquarium for AI-powered problem identification and solutions",
          "🔬 Image Analysis - Advanced recognition of coral health, algae issues, water clarity problems, and equipment setup",
          "📷 Multi-format Support - Accept images in JPG, PNG, WebP formats for comprehensive visual analysis",
          "🎯 Photo-based Product Recommendations - Get targeted AF product suggestions based on visual assessment"
        ]
      },
      {
        category: "improved",
        items: [
          "🧠 Professional AI Model - Upgraded to Google Gemini-2.5-Flash for superior intelligence and reasoning",
          "⚡ ~50% Faster Response Times - Dramatic speed improvement with more eloquent and detailed responses",
          "🎭 Enhanced Expert Personality - More knowledgeable and passionate aquarium expertise",
          "💡 Smarter Problem Analysis - Better understanding of complex aquarium chemistry and biology",
          "🔄 Improved Context Retention - Better conversation flow and follow-up understanding"
        ]
      }
    ]
  },
  {
    version: "1.3",
    date: "2025-07-02",
    type: "minor",
    title: "UI Enhancements & Performance Boost",
    description: "Major UI improvements with message management features, significant performance optimizations, and full messenger integration.",
    changes: [
      {
        category: "new",
        items: [
          "Copy message functionality - clean text without markdown formatting",
          "Download messages as PDF with professional formatting and AF branding",
          "Updates panel with comprehensive changelog history",
          "Full messenger webhook integration for seamless chat experience",
          "Mobile-responsive design with hidden avatars on small screens"
        ]
      },
      {
        category: "improved",
        items: [
          "🚀 +10-20% faster response times by removing node confidence scorer",
          "Enhanced AF AI user interface with better visual hierarchy",
          "Optimized message spacing and padding for mobile devices",
          "Better word-breaking for long texts and links",
          "Improved hamburger menu behavior - hides when sidebar is open",
          "Enhanced touch interactions and button sizing"
        ]
      },
      {
        category: "fixed",
        items: [
          "Fixed horizontal scrolling issues on mobile",
          "Resolved hamburger icon overlapping with logo",
          "Fixed textarea auto-resize behavior",
          "Prevented viewport zoom on input focus (iOS)",
          "Eliminated unnecessary 'Node: 0.0s' display during thinking"
        ]
      }
    ]
  },
  {
    version: "1.2",
    date: "2025-06-30",
    type: "minor",
    title: "🎭 Passionate Aquaforest Expert & Enhanced AI",
    description: "Revolutionary AI personality upgrade with advanced business intelligence and natural conversation flow for the ultimate aquarium experience.",
    changes: [
      {
        category: "new",
        items: [
          "🎭 Passionate Aquaforest Expert personality - enthusiastic expert who loves sharing aquarium knowledge",
          "🧠 Intelligent Business Reasoner - advanced system for selecting AF products based on your specific problems and aquarium type",
          "💬 Natural Conversation Flow - smooth conversation continuations with intelligent follow-up system",
          "🔬 ICP Analysis Results - paste your water analysis link for personalized product recommendations",
          "Advanced context memory system for better follow-up responses"
        ]
      },
      {
        category: "improved",
        items: [
          "AI responses now show genuine passion for aquaristics and reef keeping",
          "Smarter product recommendations based on aquarium type and identified problems",
          "Better understanding of follow-up questions and conversation context",
          "Enhanced multi-language support with consistent personality",
          "More detailed and educational responses about marine chemistry"
        ]
      }
    ]
  },
  {
    version: "1.1",
    date: "2025-06-16",
    type: "minor",
    title: "Enhanced AI Response System",
    description: "Improved response quality and added streaming capabilities for real-time workflow updates.",
    changes: [
      {
        category: "new",
        items: [
          "Real-time streaming workflow updates",
          "Enhanced business reasoning with mapping data",
          "Facebook Messenger full integration",
          "Advanced analytics and feedback system"
        ]
      },
      {
        category: "improved",
        items: [
          "Response formatter upgraded to VERSION 6.0 LLM INTELLIGENT",
          "Better product recommendation accuracy",
          "Faster query processing with parallel operations",
          "Enhanced multi-language support"
        ]
      }
    ]
  },
  {
    version: "1.0",
    date: "2025-06-11",
    type: "major",
    title: "Initial Release",
    description: "First stable release of AF AI Assistant with core functionality.",
    changes: [
      {
        category: "new",
        items: [
          "Core AI assistant functionality",
          "Product search and recommendations",
          "Multi-language support (PL, EN, DE, FR, ES, IT)",
          "Admin analytics panel",
          "User feedback system",
          "Authentication with access codes",
          "RAG system with Pinecone integration"
        ]
      }
    ]
  }
];

const getCategoryIcon = (category: string) => {
  switch (category) {
    case 'new':
      return <Star className="w-4 h-4 text-green-600" />;
    case 'improved':
      return <Zap className="w-4 h-4 text-blue-600" />;
    case 'fixed':
      return <Bug className="w-4 h-4 text-orange-600" />;
    case 'security':
      return <Shield className="w-4 h-4 text-red-600" />;
    default:
      return <Star className="w-4 h-4 text-gray-600" />;
  }
};

const getCategoryLabel = (category: string) => {
  switch (category) {
    case 'new':
      return 'New Features';
    case 'improved':
      return 'Improvements';
    case 'fixed':
      return 'Bug Fixes';
    case 'security':
      return 'Security';
    default:
      return 'Changes';
  }
};

const getVersionBadgeColor = (type: string) => {
  switch (type) {
    case 'major':
      return 'bg-red-100 text-red-700 border-red-200';
    case 'minor':
      return 'bg-blue-100 text-blue-700 border-blue-200';
    case 'patch':
      return 'bg-green-100 text-green-700 border-green-200';
    default:
      return 'bg-gray-100 text-gray-700 border-gray-200';
  }
};

const UpdatesPanel: React.FC = () => {
  return (
    <div className="flex-1 overflow-y-auto px-2 sm:px-4 md:px-6 pt-16 md:pt-8 pb-4 sm:pb-8">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 rounded-3xl mb-4 shadow-lg">
            <Smartphone className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold text-gray-800 mb-2">
            Updates & Changelog
          </h1>
          <p className="text-gray-600 text-sm sm:text-base">
            Track the latest improvements and features in AF AI Assistant
          </p>
        </div>

        {/* Updates Timeline */}
        <div className="space-y-8">
          {updates.map((update, index) => (
            <div key={update.version} className="relative">
              {/* Timeline line */}
              {index < updates.length - 1 && (
                <div className="absolute left-8 top-20 w-0.5 h-full bg-gradient-to-b from-purple-200 to-transparent"></div>
              )}
              
              {/* Update card */}
              <div className="bg-white/95 backdrop-blur-md rounded-3xl border border-purple-200/50 shadow-lg p-6 sm:p-8 relative">
                {/* Version badge */}
                <div className="flex items-center space-x-4 mb-4">
                  <div className="w-16 h-16 bg-gradient-to-br from-purple-600 via-purple-700 to-violet-800 rounded-2xl flex items-center justify-center shadow-lg flex-shrink-0">
                    <span className="text-white font-bold text-lg">v{update.version}</span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h2 className="text-xl sm:text-2xl font-bold text-gray-800">
                        {update.title}
                      </h2>
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getVersionBadgeColor(update.type)}`}>
                        {update.type}
                      </span>
                    </div>
                    <div className="flex items-center text-gray-500 text-sm">
                      <Calendar className="w-4 h-4 mr-2" />
                      <span>{new Date(update.date).toLocaleDateString('pl-PL', { 
                        year: 'numeric', 
                        month: 'long', 
                        day: 'numeric' 
                      })}</span>
                    </div>
                  </div>
                </div>

                {/* Description */}
                <p className="text-gray-600 mb-6 leading-relaxed">
                  {update.description}
                </p>

                {/* Changes */}
                <div className="space-y-6">
                  {update.changes.map((changeGroup, groupIndex) => (
                    <div key={groupIndex}>
                      <div className="flex items-center space-x-2 mb-3">
                        {getCategoryIcon(changeGroup.category)}
                        <h3 className="font-semibold text-gray-800">
                          {getCategoryLabel(changeGroup.category)}
                        </h3>
                      </div>
                      <ul className="space-y-2 ml-6">
                        {changeGroup.items.map((item, itemIndex) => (
                          <li key={itemIndex} className="flex items-start space-x-2">
                            <div className="w-1.5 h-1.5 bg-purple-400 rounded-full mt-2 flex-shrink-0"></div>
                            <span className="text-gray-700 text-sm leading-relaxed">
                              {item}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="text-center mt-12 p-6 bg-purple-50/50 rounded-2xl border border-purple-200/30">
          <p className="text-gray-600 text-sm">
            Have suggestions for new features? Use the{' '}
            <span className="font-semibold text-purple-700">Feedback</span> button to let us know!
          </p>
        </div>
      </div>
    </div>
  );
};

export default UpdatesPanel; 