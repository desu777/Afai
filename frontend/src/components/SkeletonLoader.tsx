import React from 'react'

interface SkeletonLoaderProps {
  variant?: 'message' | 'compact' | 'card' | 'line'
  lines?: number
  className?: string
}

const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({ 
  variant = 'message', 
  lines = 3,
  className = ''
}) => {
  const baseClasses = "animate-pulse bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 bg-[length:200%_100%] animate-[shimmer_2s_ease-in-out_infinite] rounded-lg"
  
  const renderMessageSkeleton = () => (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-start space-x-3">
        {/* Avatar skeleton */}
        <div className={`${baseClasses} w-10 h-10 rounded-2xl flex-shrink-0`}></div>
        
        {/* Message content skeleton */}
        <div className="flex-1 space-y-2">
          <div className={`${baseClasses} h-4 w-1/4`}></div>
          <div className="space-y-2">
            {Array.from({ length: lines }).map((_, index) => (
              <div 
                key={index} 
                className={`${baseClasses} h-4`}
                style={{
                  width: index === lines - 1 ? '60%' : '100%'
                }}
              ></div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )

  const renderCompactSkeleton = () => (
    <div className={`space-y-2 ${className}`}>
      {Array.from({ length: lines }).map((_, index) => (
        <div 
          key={index} 
          className={`${baseClasses} h-4`}
          style={{
            width: index === 0 ? '90%' : index === lines - 1 ? '75%' : '100%'
          }}
        ></div>
      ))}
    </div>
  )

  const renderCardSkeleton = () => (
    <div className={`p-6 border rounded-xl bg-white shadow-sm ${className}`}>
      <div className="space-y-4">
        <div className={`${baseClasses} h-6 w-3/4`}></div>
        <div className="space-y-2">
          {Array.from({ length: lines }).map((_, index) => (
            <div 
              key={index} 
              className={`${baseClasses} h-4`}
              style={{
                width: index === lines - 1 ? '60%' : '100%'
              }}
            ></div>
          ))}
        </div>
        <div className="flex space-x-2">
          <div className={`${baseClasses} h-8 w-16`}></div>
          <div className={`${baseClasses} h-8 w-20`}></div>
        </div>
      </div>
    </div>
  )

  const renderLineSkeleton = () => (
    <div className={`${baseClasses} h-4 w-full ${className}`}></div>
  )

  switch (variant) {
    case 'message':
      return renderMessageSkeleton()
    case 'compact':
      return renderCompactSkeleton()
    case 'card':
      return renderCardSkeleton()
    case 'line':
      return renderLineSkeleton()
    default:
      return renderMessageSkeleton()
  }
}

export default SkeletonLoader