import React, { useState, useEffect } from 'react'

const SkeletonLoadingMessage: React.FC = () => {
  const [currentPhase, setCurrentPhase] = useState(0)

  const phases = [
    { lines: 1, duration: 1000 },
    { lines: 2, duration: 1500 },
    { lines: 3, duration: 2000 },
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentPhase(prev => (prev + 1) % phases.length)
    }, phases[currentPhase].duration)

    return () => clearInterval(interval)
  }, [currentPhase])

  return (
    <div className="flex justify-start mb-4 sm:mb-6">
      <div className="flex items-start space-x-2 sm:space-x-4 max-w-[90%] sm:max-w-3xl w-full">
        {/* Avatar - hidden on mobile */}
        <div className="hidden sm:flex w-10 h-10 rounded-lg bg-brand-600 items-center justify-center shadow-sm flex-shrink-0">
          <div className="circle">
            <div className="wave"></div>
          </div>
        </div>
        
        {/* Skeleton content */}
        <div className="rounded-lg sm:rounded-lg px-4 py-3 sm:px-6 sm:py-4 bg-white/95 backdrop-blur-md border border-purple-200/40 shadow-sm flex-1 min-w-0">
          <div className="space-y-3">
            {/* Status indicator */}
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-brand-600 rounded-full animate-pulse"></div>
              <span className="text-body text-xs text-gray-500 font-medium">
                Afai is thinking...
              </span>
            </div>
            
            {/* Progressive skeleton loading */}
            <div className="space-y-2">
              {Array.from({ length: phases[currentPhase].lines }).map((_, index) => (
                <div 
                  key={index}
                  className="h-4 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 rounded-lg animate-shimmer"
                  style={{
                    width: index === phases[currentPhase].lines - 1 ? '70%' : '100%',
                    backgroundSize: '200% 100%'
                  }}
                ></div>
              ))}
            </div>
            
            {/* Typing indicator */}
            <div className="flex items-center space-x-1">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-brand-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default SkeletonLoadingMessage