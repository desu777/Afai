import { Fish, Settings, MoreVertical } from 'lucide-react'

const Header: React.FC = () => {
  return (
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
  );
};

export default Header 