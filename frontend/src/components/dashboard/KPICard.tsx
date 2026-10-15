import clsx from 'clsx'
import { TrendingUp, TrendingDown } from 'lucide-react'
import { Card, CardBody } from '@/components/ui/Card'
import { SkeletonCard } from '@/components/ui/Skeleton'

interface KPICardProps {
  label: string
  value: number | string
  change?: number // positive or negative percentage
  changeLabel?: string
  variant?: 'default' | 'critical' | 'high' | 'medium' | 'low'
  isLoading?: boolean
}

const borderColorMap = {
  default: 'border-l-gray-300',
  critical: 'border-l-risk-critical',
  high: 'border-l-risk-high',
  medium: 'border-l-risk-medium',
  low: 'border-l-risk-low',
}

const textColorMap = {
  default: 'text-gray-600',
  critical: 'text-risk-critical',
  high: 'text-risk-high',
  medium: 'text-risk-medium',
  low: 'text-risk-low',
}

export const KPICard = ({
  label,
  value,
  change,
  changeLabel = 'vs last week',
  variant = 'default',
  isLoading = false,
}: KPICardProps) => {
  if (isLoading) return <SkeletonCard />

  const isPositive = change ? change >= 0 : undefined

  return (
    <Card className={clsx('border-l-4', borderColorMap[variant])}>
      <CardBody className="space-y-3">
        <p className="text-sm text-gray-600">{label}</p>
        <div className="flex items-baseline gap-2">
          <p className={clsx('text-4xl font-bold', textColorMap[variant])}>{value}</p>
          {change !== undefined && (
            <div className={clsx('flex items-center gap-1 text-sm', isPositive ? 'text-green-600' : 'text-red-600')}>
              {isPositive ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
              <span>{Math.abs(change)}%</span>
            </div>
          )}
        </div>
        {changeLabel && <p className="text-xs text-gray-500">{changeLabel}</p>}
      </CardBody>
    </Card>
  )
}
