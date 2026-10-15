import { z } from 'zod'

export const riskFormSchema = z.object({
  title: z.string().min(5, 'Title must be at least 5 characters').max(100, 'Title must be less than 100 characters'),
  description: z
    .string()
    .min(20, 'Description must be at least 20 characters')
    .max(500, 'Description must be less than 500 characters'),
  category: z.enum(['Financial', 'HR', 'Academic', 'IT', 'Compliance', 'Operational', 'Reputational']),
  departmentId: z.string().min(1, 'Department is required'),
  ownerId: z.string().uuid('Select a valid risk owner'),
  status: z.enum(['Draft', 'Open', 'In-Progress', 'Mitigated', 'Closed', 'Escalated', 'Pending Approval', 'Approved', 'Rejected']),
  likelihood: z.number().int().min(1, 'Likelihood must be 1-5').max(5, 'Likelihood must be 1-5'),
  impact: z.number().int().min(1, 'Impact must be 1-5').max(5, 'Impact must be 1-5'),
  velocity: z.number().int().min(1, 'Velocity must be 1-5').max(5, 'Velocity must be 1-5'),
  detectability: z.number().int().min(1, 'Detectability must be 1-5').max(5, 'Detectability must be 1-5'),
})

export type RiskFormData = z.infer<typeof riskFormSchema>

export const calculateRiskScore = (likelihood: number, impact: number, velocity: number, detectability: number) => {
  const raw = likelihood * impact * velocity * detectability
  const normalized = Math.round((raw / 625) * 100)
  return Math.min(100, normalized)
}

export const getSeverityBand = (score: number): 'critical' | 'high' | 'medium' | 'low' => {
  if (score >= 75) return 'critical'
  if (score >= 50) return 'high'
  if (score >= 25) return 'medium'
  return 'low'
}
