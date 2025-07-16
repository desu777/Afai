import { useState, useCallback } from 'react'
import { ToastProps } from '../components/Toast'

export interface ToastConfig {
  title: string
  message?: string
  duration?: number
}

export interface UseToastReturn {
  toasts: ToastProps[]
  showToast: (type: ToastProps['type'], config: ToastConfig) => void
  showSuccess: (config: ToastConfig) => void
  showError: (config: ToastConfig) => void
  showWarning: (config: ToastConfig) => void
  showInfo: (config: ToastConfig) => void
  dismissToast: (id: string) => void
  clearAllToasts: () => void
}

export const useToast = (): UseToastReturn => {
  const [toasts, setToasts] = useState<ToastProps[]>([])

  const generateId = useCallback(() => {
    return Math.random().toString(36).substr(2, 9)
  }, [])

  const showToast = useCallback((type: ToastProps['type'], config: ToastConfig) => {
    const id = generateId()
    const toast: ToastProps = {
      id,
      type,
      title: config.title,
      message: config.message,
      duration: config.duration || 5000,
      onClose: dismissToast
    }
    
    setToasts(prev => [...prev, toast])
    
    // Auto-remove after duration
    setTimeout(() => {
      dismissToast(id)
    }, toast.duration)
  }, [generateId])

  const dismissToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])

  const clearAllToasts = useCallback(() => {
    setToasts([])
  }, [])

  const showSuccess = useCallback((config: ToastConfig) => {
    showToast('success', config)
  }, [showToast])

  const showError = useCallback((config: ToastConfig) => {
    showToast('error', config)
  }, [showToast])

  const showWarning = useCallback((config: ToastConfig) => {
    showToast('warning', config)
  }, [showToast])

  const showInfo = useCallback((config: ToastConfig) => {
    showToast('info', config)
  }, [showToast])

  return {
    toasts,
    showToast,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    dismissToast,
    clearAllToasts
  }
}