import { ReactNode } from 'react'
import clsx from 'clsx'
import { RiskSeverity, RiskStatus } from '@/types'
import { riskBgColorMap } from '@/utils/riskColor'

type BadgeVariant = RiskSeverity | 'default' | 'success' | 'warning' | 'error'

interface BadgeProps {
  variant?: BadgeVariant
  children: ReactNode
  className?: string
}

const variantStyles: Record<string, string> = {
  critical: `${riskBgColorMap.critical} text-white`,
  high: `${riskBgColorMap.high} text-white`,
  medium: `${riskBgColorMap.medium} text-white`,
  low: `${riskBgColorMap.low} text-white`,
  default: 'bg-gray-200 text-gray-900',
  success: 'bg-green-100 text-green-900',
  warning: 'bg-yellow-100 text-yellow-900',
  error: 'bg-red-100 text-red-900',
}

export const Badge = ({ variant = 'default', children, className }: BadgeProps) => {
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        variantStyles[variant] || variantStyles.default,
        className
      )}
    >
      {children}
    </span>
  )
}

const statusStyleMap: Record<RiskStatus, string> = {
  draft: 'bg-gray-100 text-gray-800',
  pending_approval: 'bg-amber-100 text-amber-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  open: 'bg-blue-100 text-blue-800',
  monitoring: 'bg-orange-100 text-orange-800',
  mitigated: 'bg-teal-100 text-teal-800',
  closed: 'bg-gray-100 text-gray-600',
}

const statusLabelMap: Record<RiskStatus, string> = {
  draft: 'Draft',
  pending_approval: 'Pending Approval',
  approved: 'Approved',
  rejected: 'Rejected',
  open: 'Open',
  monitoring: 'In-Progress',
  mitigated: 'Mitigated',
  closed: 'Closed',
}

interface StatusBadgeProps {
  status: RiskStatus
  className?: string
}

export const StatusBadge = ({ status, className }: StatusBadgeProps) => {
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        statusStyleMap[status] || 'bg-gray-100 text-gray-800',
        className
      )}
    >
      {statusLabelMap[status] || status}
    </span>
  )
}
