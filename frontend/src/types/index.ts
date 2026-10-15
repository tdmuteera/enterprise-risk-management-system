// Auth
export interface User {
  id: string
  email: string
  name: string
  role:
    | 'admin'
    | 'risk_officer'
    | 'dept_user'
    | 'data_clerk'
    | 'risk_clerk'
    | 'executive'
    | 'risk_manager'
    | 'department_head'
    | 'viewer'
  departmentId?: string
  department_id?: string
  createdAt?: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
  role?: 'risk_officer' | 'dept_user' | 'data_clerk' | 'risk_clerk'
  department_id?: string
}

export interface AuthResponse {
  token: string
  user: User
}

// Departments
export interface Department {
  id: string
  name: string
  code: string
  head: string
  riskScore: number
  riskLevel: 'critical' | 'high' | 'medium' | 'low'
  createdAt: string
}

// Risks
export type RiskSeverity = 'critical' | 'high' | 'medium' | 'low'
export type RiskStatus = 'open' | 'mitigated' | 'closed' | 'monitoring' | 'draft' | 'pending_approval' | 'approved' | 'rejected'

export interface Risk {
  id: string
  title: string
  description: string
  category: string
  departmentId: string
  severity: RiskSeverity
  probability: number // 1-5 (likelihood)
  impact: number // 1-5
  velocity?: number
  detectability?: number
  riskScore: number
  status: RiskStatus
  /** Original API status label for forms (e.g. In-Progress, Escalated). */
  apiStatus?: string
  riskType?: 'Inherent' | 'Residual'
  parentRiskId?: string
  reviewerId?: string
  reviewJustification?: string
  reviewedAt?: string
  owner: string
  createdAt: string
  updatedAt: string
  dependencies?: string[] // Risk IDs
}

export interface RiskCreateRequest {
  title: string
  description: string
  category: string
  departmentId: string
  probability: number
  impact: number
  owner: string
}

export interface RiskUpdateRequest {
  title?: string
  description?: string
  probability?: number
  impact?: number
  status?: RiskStatus
}

// Mitigations
export interface Mitigation {
  id: string
  riskId: string
  title: string
  description: string
  owner: string
  dueDate: string
  status: 'not_started' | 'in_progress' | 'completed'
  effectiveness: number // 1-100
  createdAt: string
}

export interface MitigationCreateRequest {
  riskId: string
  title: string
  description: string
  owner: string
  dueDate: string
}

// Alerts
export interface Alert {
  id: string
  riskId: string
  title: string
  message: string
  severity: RiskSeverity
  read: boolean
  createdAt: string
}

// Reports
export interface Report {
  id: string
  title: string
  type: 'executive' | 'departmental' | 'compliance' | 'forensic'
  departmentId?: string
  generatedAt: string
  generatedBy: string
  format: 'pdf' | 'excel' | 'json'
  url: string
}

// Audit
export interface AuditLog {
  id: string
  userId: string
  action: string
  entity: string
  entityId: string
  changes: Record<string, unknown>
  timestamp: string
}

// Analytics/Dashboard
export interface DashboardStats {
  totalRisks: number
  criticalCount: number
  highCount: number
  mediumCount: number
  lowCount: number
  averageRiskScore: number
  openMitigations: number
}

export interface RiskTrendData {
  date: string
  count: number
  severity: RiskSeverity
}

export interface HeatmapCell {
  probability: number
  impact: number
  count: number
  risks: Risk[]
}
