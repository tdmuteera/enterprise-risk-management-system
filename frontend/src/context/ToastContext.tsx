import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react'
import { registerToastHandler } from '@/lib/toastBridge'
import { AlertCircle, CheckCircle, AlertTriangle, Info, X } from 'lucide-react'
import clsx from 'clsx'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

interface Toast {
  id: string
  type: ToastType
  message: string
  duration?: number
}

interface ToastContextType {
  toasts: Toast[]
  addToast: (message: string, type?: ToastType, duration?: number) => void
  removeToast: (id: string) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export const ToastProvider = ({ children }: { children: ReactNode }) => {
  const [toasts, setToasts] = useState<Toast[]>([])

  const addToast = useCallback((message: string, type: ToastType = 'info', duration = 4000) => {
    const id = Date.now().toString()
    const newToast: Toast = { id, type, message, duration }

    setToasts((prev) => {
      const updated = [...prev, newToast]
      // Keep only last 3 toasts
      return updated.slice(-3)
    })

    // Auto-dismiss
    const timeout = setTimeout(() => {
      removeToast(id)
    }, duration)

    return () => clearTimeout(timeout)
  }, [])

  useEffect(() => {
    registerToastHandler(addToast)
    return () => registerToastHandler(null)
  }, [addToast])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  )
}

export const useToast = () => {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return context
}

const ToastContainer = () => {
  const { toasts, removeToast } = useToast()

  const iconMap = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info,
  }

  const colorMap = {
    success: 'bg-green-50 border-green-200 text-green-900',
    error: 'bg-red-50 border-red-200 text-red-900',
    warning: 'bg-amber-50 border-amber-200 text-amber-900',
    info: 'bg-blue-50 border-blue-200 text-blue-900',
  }

  const iconColorMap = {
    success: 'text-green-600',
    error: 'text-red-600',
    warning: 'text-amber-600',
    info: 'text-blue-600',
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {toasts.map((toast) => {
        const Icon = iconMap[toast.type]
        return (
          <div
            key={toast.id}
            className={clsx(
              'relative rounded-lg border p-4 pr-12 shadow-lg flex gap-3 items-start max-w-sm animate-in slide-in-from-right-5',
              colorMap[toast.type]
            )}
          >
            <Icon className={clsx('mt-0.5 flex-shrink-0', iconColorMap[toast.type])} size={20} />
            <p className="text-sm font-medium flex-1">{toast.message}</p>
            <button
              type="button"
              onClick={() => removeToast(toast.id)}
              className="absolute top-3 right-3 z-10 opacity-50 hover:opacity-100 transition-opacity"
            >
              <X size={16} />
            </button>
          </div>
        )
      })}
    </div>
  )
}
