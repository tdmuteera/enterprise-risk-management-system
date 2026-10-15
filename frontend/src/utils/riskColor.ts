import { RiskSeverity } from '@/types'

export const riskColorMap: Record<RiskSeverity, string> = {
  critical: '#D32F2F',
  high: '#F57C00',
  medium: '#FBC02D',
  low: '#388E3C',
}

export const riskBgColorMap: Record<RiskSeverity, string> = {
  critical: 'bg-risk-critical',
  high: 'bg-risk-high',
  medium: 'bg-risk-medium',
  low: 'bg-risk-low',
}

export const riskTextColorMap: Record<RiskSeverity, string> = {
  critical: 'text-risk-critical',
  high: 'text-risk-high',
  medium: 'text-risk-medium',
  low: 'text-risk-low',
}

export const riskBadgeVariantMap: Record<RiskSeverity, 'critical' | 'high' | 'medium' | 'low'> = {
  critical: 'critical',
  high: 'high',
  medium: 'medium',
  low: 'low',
}

export const getRiskColor = (severity: RiskSeverity): string => {
  return riskColorMap[severity]
}

export const getRiskBgClass = (severity: RiskSeverity): string => {
  return riskBgColorMap[severity]
}

export const getRiskTextClass = (severity: RiskSeverity): string => {
  return riskTextColorMap[severity]
}

export const calculateRiskScore = (probability: number, impact: number): number => {
  return probability * impact
}

export const getSeverityFromScore = (score: number): RiskSeverity => {
  if (score >= 20) return 'critical'
  if (score >= 12) return 'high'
  if (score >= 6) return 'medium'
  return 'low'
}
