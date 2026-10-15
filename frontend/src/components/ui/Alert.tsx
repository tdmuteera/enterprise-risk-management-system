import { ReactNode } from 'react'
import clsx from 'clsx'
import { AlertCircle, CheckCircle2, AlertTriangle, Info, X } from 'lucide-react'

interface AlertProps {
  variant?: 'success' | 'error' | 'warning' | 'info'
  title?: string
  message: ReactNode
  onClose?: () => void
  className?: string
}

const iconMap = {
  success: CheckCircle2,
  error: AlertCircle,
  warning: AlertTriangle,
  info: Info,
}

const bgColorMap = {
  success: 'bg-green-50 border-green-200',
  error: 'bg-red-50 border-red-200',
  warning: 'bg-yellow-50 border-yellow-200',
  info: 'bg-blue-50 border-blue-200',
}

const textColorMap = {
  success: 'text-green-800',
  error: 'text-red-800',
  warning: 'text-yellow-800',
  info: 'text-blue-800',
}

const iconColorMap = {
  success: 'text-green-600',
  error: 'text-red-600',
  warning: 'text-yellow-600',
  info: 'text-blue-600',
}

export const Alert = ({
  variant = 'info',
  title,
  message,
  onClose,
  className,
}: AlertProps) => {
  const Icon = iconMap[variant]

  return (
    <div
      className={clsx(
        'rounded-lg border p-4 flex gap-3',
        bgColorMap[variant],
        textColorMap[variant],
        className
      )}
    >
      <Icon className={clsx('h-5 w-5 mt-0.5 flex-shrink-0', iconColorMap[variant])} />
      <div className="flex-1">
        {title && <h3 className="font-medium mb-1">{title}</h3>}
        <p className="text-sm">{message}</p>
      </div>
      {onClose && (
        <button
          type="button"
          onClick={onClose}
          className="flex-shrink-0 ml-2 hover:opacity-70 transition-opacity"
        >
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  )
}
