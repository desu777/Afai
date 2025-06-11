import { Send, Sparkles } from 'lucide-react'

interface SuggestedQueriesProps {
  onQuerySelect: (query: string) => void;
}

const SuggestedQueries: React.FC<SuggestedQueriesProps> = ({ onQuerySelect }) => {
  const suggestedQueries = [
    "How to raise calcium levels?",
    "Algae problems solutions",
    "AF Build dosing guide",
    "Products for beginners"
  ];

  return (
    <div className="text-center mb-12">
      <div className="inline-flex items-center space-x-3 bg-white/80 backdrop-blur-md rounded-2xl px-8 py-4 shadow-lg border border-purple-200/50 mb-8">
        <Sparkles className="w-6 h-6 text-purple-600" />
        <span className="text-gray-800 font-semibold text-lg">Start conversation with AF AI</span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mx-auto">
        {suggestedQueries.map((query, index) => (
          <button
            key={index}
            onClick={() => onQuerySelect(query)}
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
  );
};

export default SuggestedQueries 