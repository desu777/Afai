import React, { useEffect, useState } from 'react'
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react'

export interface ToastProps {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
  onClose: (id: string) => void
}

const Toast: React.FC<ToastProps> = ({ 
  id, 
  type, 
  title, 
  message, 
  duration = 5000, 
  onClose 
}) => {
  const [isVisible, setIsVisible] = useState(false)
  const [isExiting, setIsExiting] = useState(false)

  useEffect(() => {
    // Entrance animation
    const timer = setTimeout(() => setIsVisible(true), 100)
    
    // Auto-dismiss
    const dismissTimer = setTimeout(() => {
      handleClose()
    }, duration)

    return () => {
      clearTimeout(timer)
      clearTimeout(dismissTimer)
    }
  }, [duration])

  const handleClose = () => {
    setIsExiting(true)
    setTimeout(() => {
      onClose(id)
    }, 300)
  }

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-success-600" />
      case 'error':
        return <XCircle className="w-5 h-5 text-error-600" />
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-warning-600" />
      case 'info':
        return <Info className="w-5 h-5 text-brand-600" />
      default:
        return <Info className="w-5 h-5 text-brand-600" />
    }
  }

  const getStyles = () => {
    const baseStyles = "border-l-4 bg-white shadow-lg rounded-lg p-4 pointer-events-auto"
    
    switch (type) {
      case 'success':
        return `${baseStyles} border-success-500 shadow-success-500/10`
      case 'error':
        return `${baseStyles} border-error-500 shadow-error-500/10`
      case 'warning':
        return `${baseStyles} border-warning-500 shadow-warning-500/10`
      case 'info':
        return `${baseStyles} border-brand-500 shadow-brand-500/10`
      default:
        return `${baseStyles} border-brand-500 shadow-brand-500/10`
    }
  }

  return (
    <div
      className={`
        transform transition-all duration-300 ease-out
        ${isVisible && !isExiting ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}
        ${isExiting ? 'scale-95' : 'scale-100'}
        max-w-md w-full
      `}
    >
      <div className={getStyles()}>
        <div className="flex items-start space-x-3">
          {/* Icon */}
          <div className="flex-shrink-0">
            {getIcon()}
          </div>
          
          {/* Content */}
          <div className="flex-1 min-w-0">
            <h4 className="text-display text-sm font-semibold text-gray-900 mb-1">
              {title}
            </h4>
            {message && (
              <p className="text-body text-sm text-gray-600 leading-relaxed">
                {message}
              </p>
            )}
          </div>
          
          {/* Close button */}
          <button
            onClick={handleClose}
            className="flex-shrink-0 p-1 hover:bg-gray-100 rounded-lg transition-colors duration-200"
            aria-label="Close notification"
          >
            <X className="w-4 h-4 text-gray-400 hover:text-gray-600" />
          </button>
        </div>
        
        {/* Progress bar */}
        <div className="mt-3 h-1 bg-gray-100 rounded-full overflow-hidden">
          <div 
            className={`h-full bg-gradient-to-r ${
              type === 'success' ? 'from-success-500 to-success-600' :
              type === 'error' ? 'from-error-500 to-error-600' :
              type === 'warning' ? 'from-warning-500 to-warning-600' :
              'from-brand-500 to-brand-600'
            } rounded-full transition-all duration-300 ease-out`}
            style={{
              animation: `shrink ${duration}ms linear forwards`,
              width: '100%'
            }}
          />
        </div>
      </div>
    </div>
  )
}

export default Toast